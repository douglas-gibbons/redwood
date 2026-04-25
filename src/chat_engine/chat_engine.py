from importlib.resources import contents
import json
import os
from google import genai
from .display_interface import DisplayInterface
import mcp_client
import logging
from config import Config
import asyncio

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.config/redwood/redwood.yaml")

logging.getLogger().handlers.clear()
logger = logging.getLogger(__name__)

class ChatEngine:

    def __init__(self, display: DisplayInterface):
        self.display = display
        logger.info("Starting redwood main")
        
        # Load config file
        self.config = Config(DEFAULT_CONFIG_FILE)
        
        # Gemini model name
        self.model_name = self.config.model.name

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=self.config.logging.level,
            filemode='a',
            filename=self.config.logging.file
        )

        # Chat contents
        self.contents = []

        # MCP servers
        self.mcp_servers = []

        self.model_calls: int = 0


    async def setup_api_key(self):
        await self.display.error("API key not found in config file.")
        await self.display.markdown("""
To use Redwood, you need to provide an API key for the Gemini model.
                                    
You can get an API key at [aistudio.google.com/api-keys](https://aistudio.google.com/api-keys).
""")
        api_key = await self.display.ask_question("Please enter a Gemini API key. You can get create new API key at [aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)")
        if not api_key:
            await self.display.error("No API key provided.")
            await self.exit()
            return
        
        self.config.write_api_key(api_key)
        await self.display.info("API key saved to config file.")
        
        # Reload config
        self.config = Config(DEFAULT_CONFIG_FILE)

    async def initialize(self):

        if not self.config.exists("model.api_key") or self.config.model.api_key == "API-KEY-HERE":
            await self.setup_api_key()
            
        if not self.config.exists("model.api_key") or self.config.model.api_key == "API-KEY-HERE":
            return

        # set up connetion to Gemini and MCP servers
        self.gclient = genai.Client(api_key=self.config.model.api_key)
        
        await self.display.info("Welcome to Redwood!")
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.print_help())
            tg.create_task(self.register_tools())
        await self.display.markdown(f"Using model: `{self.model_name}`")

    async def print_tools(self, tools: list):
        
        output = ""
        output += "# Available Tools:\n"
        tools_by_server = {}
        for tool in tools:
            server_name, tool_name = mcp_client.get_tool_name(tool.name)
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            tools_by_server[server_name].append((tool_name, tool))
        
        for server_name, server_tools in tools_by_server.items():
            output += f"## Server: {server_name}\n"
            for tool_name, tool in server_tools:
                output += f"###  {tool_name}\n"
                if tool.description:
                    output += f"{tool.description}\n"
                # if tool.inputSchema:
                #   output += f"Args: {tool.inputSchema}\n"
        await self.display.markdown(output)
                
    async def set_location(self, contents):
        location = os.getcwd()
        await self.display.info(f"Location set to {location}")
        contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=f"Use \"{location}\" as the working directory. File operations should be relative to this directory.")]))
        contents.append(genai.types.Content(role="model", parts=[genai.types.Part(text="Understood")]))
        
    async def print_conversation(self, contents):
        await self.display.info("Conversation History:")
        await self.display.markdown(f"```{contents}```")

    async def set_initial_prompt(self):
        # Set initial prompt
        # Gemini only has user and system prompts
        if self.config.exists("prompt"):
            self.contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=self.config.prompt)]))
            self.contents.append(genai.types.Content(role="model", parts=[genai.types.Part(text="Understood")]))

    async def print_help(self):
        await self.display.markdown("""
You can interact with the AI model and use various tools via MCP servers by typing these commands:                              

```
Tools:        '/tools', or '/t' to list available tools
Reset:        '/reset', or '/r' to reset the conversation
Conversation: '/conversation' or '/c' to show conversation history
Locate:       '/locate' or '/l' to tell the model to work in the current directory
Help:         '/help' or '/?' to show this help message
Exit:         '/exit' or '/x' to quit
```

You can find the configuration file at `~/.config/redwood/redwood.yaml`. Feel free to modify it manually 
or simply instruct the agent to handle the updates for you. For instance, you could ask it to disable 
tool execution prompts or request a rundown of all available configuration settings.
                                    
If you want to know what Redwood can do, just ask :)
""")

    async def register_tools(self):
        
        self.mcp_servers = []
        for server_config in self.config.mcp:
            server = mcp_client.dict_to_server(server_config)
            self.mcp_servers.append(server)
        
        token_storage_config = None
        if self.config.exists("token_storage.enabled") and self.config.token_storage.enabled:
            token_storage_config = mcp_client.TokenStorageConfig(
                enabled = self.config.token_storage.enabled,
                location = os.path.expanduser(self.config.token_storage.location),
                encryption_key = self.config.token_storage.encryption_key
            )
        self.mcpc = mcp_client.MCPClient(
            display=self.display,
            servers=self.mcp_servers, 
            log_file=self.config.logging.file, 
            token_storage_config=token_storage_config
        )
        
        self.tools = await self.mcpc.list_tools()
        await self.set_initial_prompt()

        self.gemini_config = genai.types.GenerateContentConfig(
            tools = self.tools,
            automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )
        
    async def exit(self):
        await self.display.info("Goodbye!")
        await self.display.quit()

    async def reset_conversation(self):
        self.contents.clear()
        self.model_calls = 0
        await self.set_initial_prompt()
        await self.display.info("Conversation history reset")

    async def _handle_command(self, user_input: str) -> bool:

        """Handles slash commands. Returns True if a command was processed."""
        if user_input == "/exit" or user_input == "/x":
            await self.exit()
        elif user_input == "/tools" or user_input == "/t":
            await self.print_tools(self.tools)
        elif user_input == "/conversation" or user_input == "/c":
            await self.print_conversation(self.contents)
        elif user_input == "/locate" or user_input == "/l":
            await self.set_location(self.contents)
        elif user_input == "/help" or user_input == "/?":
            await self.print_help()
        elif user_input == "/reset" or user_input == "/r":
            await self.reset_conversation()
        else:
            return False
        return True

    async def answer_call(self, user_input: str | None = None):        
        logger.debug(f"answer_call received message: {user_input}")

        if user_input is not None and user_input.startswith("/"):
            await self._handle_command(user_input)
            return

        if user_input is not None:
            # Append user output to contents
            self.contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=user_input)]))
        

        # Safety valve
        if self.model_calls >= int(self.config.max_model_calls):
            await self.display.warn("Max model calls reached")
            await self.display.info("This is a safety valve to catch costly looping. You can increase the limit in the config file if needed.")
            await self.exit()        

        self.model_calls += 1

        # Call LLM
        try:
            response = await self.gclient.aio.models.generate_content(
                model = self.model_name,
                contents = self.contents,
                config = self.gemini_config
            )
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            await self.display.error(e.message)
            return

        # Append LLM output to contents
        self.contents.append(response.candidates[0].content)

        if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
            await self.display.warn("*No content returned from model.*")
            logger.warning(f"No content returned from model. Full response: {response}")
            return

        function_calls = []
        texts = []

        # process model response
        for part in response.candidates[0].content.parts:

            # Model wants to call a function
            if part.function_call:
                function_calls.append(part.function_call)

            # Model returned text
            elif part.text:
                texts.append(part.text)
            
            # Who knows what the model returned? Not I.
            else:
                await self.display.warn("Unknown part")

        for text in texts:
            await self.display.markdown(text)

        if function_calls:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(self.call_tool(fc.name, fc.args))
                    for fc in function_calls
                ]
            
            function_parts = []
            for task in tasks:
                content_resp = task.result()
                function_parts.extend(content_resp.parts)
            
            self.contents.append(genai.types.Content(role="function", parts=function_parts))
            
            # Loop back to get the model's response to the tool outputs
            await self.answer_call()

    async def call_tool(self, tool_name: str, args: dict) -> genai.types.Content:
        # Format the arguments for better readability
        try:
            if hasattr(args, "model_dump"):
                formatted_args = json.dumps(args.model_dump(), indent=2)
            elif type(args) is dict:
                formatted_args = json.dumps(args, indent=2)
            else:
                formatted_args = json.dumps(dict(args), indent=2)
        except Exception:
            formatted_args = str(args)
            
        await self.display.tool_log(f"**Call:** `{tool_name}`\n```json\n{formatted_args}\n```")
        
        response = await self.mcpc.execute_tool(tool_name, args)
        
        # Format the response for better readability
        try:
            if hasattr(response, "model_dump"):
                formatted_response = json.dumps(response.model_dump(), indent=2)
            elif hasattr(response, "__dict__"):
                formatted_response = json.dumps(response.__dict__, indent=2, default=str)
            elif isinstance(response, dict) and "result" in response and len(response) == 1:
                formatted_response = str(response["result"])
            else:
                formatted_response = json.dumps(response, indent=2)
        except Exception:
            formatted_response = str(response)
            
        # Truncate response if it's too long
        if len(formatted_response) > 2000:
            formatted_response = formatted_response[:2000] + "\n... [truncated]"
            
        if isinstance(response, dict) and "result" in response and len(response) == 1:
            await self.display.tool_log(f"**Result:**\n```\n{formatted_response}\n```")
        else:
            await self.display.tool_log(f"**Result:**\n```json\n{formatted_response}\n```")
        
        function_response_part = genai.types.Part.from_function_response(
            name = tool_name,
            response=response
        )
        resp = genai.types.Content(role="function", parts=[function_response_part])
        return resp
