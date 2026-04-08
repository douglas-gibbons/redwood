from importlib.resources import contents
import json
import os
from google import genai
from rich.markdown import Markdown
from .display_interface import DisplayInterface
import mcp_client
import pprint
import logging
from config import Config
import sys

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.config/redwood.yaml")

logging.getLogger().handlers.clear()
logger = logging.getLogger(__name__)

class ChatEngine:

    def __init__(self, display: DisplayInterface):
        self.display = display
        logger.info("Starting redwood main")
        
        self.display.info("Welcome to Redwood!")
        self.print_help()

        # Load config file
        self.config = Config(DEFAULT_CONFIG_FILE)

        if not self.config.exists("model.api_key"):
            raise ValueError("API Key missing from configuration file")

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=self.config.logging.level,
            filemode='a',
            filename=self.config.logging.file
        )

        self.gclient = genai.Client(api_key=self.config.model.api_key)

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
        self.mcpc = mcp_client.MCPClient(servers=self.mcp_servers, log_file=self.config.logging.file, token_storage_config=token_storage_config)
        
        # Gemini model name
        self.model_name = self.config.model.name
        self.display.markdown(f"Using model: `{self.model_name}`")

        # Chat contents
        self.contents = []

        self.model_calls: int = 0

    def print_tools(self, tools: list):
        
        self.display.markdown("Available Tools:")
        tools_by_server = {}
        for tool in tools:
            server_name, tool_name = mcp_client.get_tool_name(tool.name)
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            tools_by_server[server_name].append((tool_name, tool))
        
        for server_name, server_tools in tools_by_server.items():
            self.display.markdown(f"## Server: {server_name}")
            for tool_name, tool in server_tools:
                self.display.markdown(f"###  {tool_name}")
                if tool.description:
                    self.display.markdown(f"_{tool.description}_")
                if tool.inputSchema:
                    self.display.markdown(f"Args: {tool.inputSchema}")

    def set_location(self, contents):
        location = os.getcwd()
        self.display.info(f"Location set to {location}")
        contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=f"Use \"{location}\" as the working directory. File operations should be relative to this directory.")]))
        contents.append(genai.types.Content(role="model", parts=[genai.types.Part(text="Understood")]))
        
    def print_conversation(self, contents):
        self.display.info("Conversation History:")
        self.display.markdown(f"```{contents}```")

    def set_initial_prompt(self):
        # Set initial prompt
        # Gemini only has user and system prompts
        if self.config.exists("prompt"):
            self.contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=self.config.prompt)]))
            self.contents.append(genai.types.Content(role="model", parts=[genai.types.Part(text="Understood")]))

    def print_help(self):
        self.display.markdown("""
```
You can interact with the AI model and use various tools via MCP servers by typing these commands:                              

Tools:        '/tools', or '/t' to list available tools
Reset:        '/reset', or '/r' to reset the conversation
Conversation: '/conversation' or '/c' to show conversation history
Locate:       '/locate' or '/l' to tell the model to work in the current directory
Help:         '/help' or '/?' to show this help message
Exit:         '/exit' or '/x' to quit
```

        """)

        
    async def register_tools(self):
        self.tools = await self.mcpc.list_tools()
        self.set_initial_prompt()

        self.gemini_config = genai.types.GenerateContentConfig(
            tools = self.tools,
            automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )
        

    def exit(self):
        self.display.info("Goodbye!")
        sys.exit(0)

    async def answer_call(self, user_input: str):
        
        logger.debug(f"answer_call received message: {user_input}")
                        
        # Safety valve
        if self.model_calls >= int(self.config.max_model_calls):
            self.display.warn("Max model calls reached")
            self.display.info("This is a safety valve to catch costly looping. You can increase the limit in the config file if needed.")
            self.exit()        
        self.model_calls += 1


        if user_input == "/exit" or user_input == "/x":
            self.exit()
            
        elif user_input == "/tools" or user_input == "/t":
            self.print_tools(self.tools)
            
        elif user_input == "/conversation" or user_input == "/c":
            self.print_conversation(self.contents)
            
        elif user_input == "/locate" or user_input == "/l":
            self.set_location(self.contents)
            
        elif user_input == "/help" or user_input == "/?":
            self.print_help()
            
        elif user_input == "/reset" or user_input == "/r":
            self.contents.clear()
            self.set_initial_prompt(self.contents, self.config)
            self.display.info("Conversation history reset")

        elif user_input:
            # Append user output to contents
            self.contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=user_input)]))

        # Call LLM
        response = self.gclient.models.generate_content(
            model = self.model_name,
            contents = self.contents,
            config = self.gemini_config
        )

        # Append LLM output to contents
        self.contents.append(response.candidates[0].content)

        # Check for empty response
        if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
            self.display.warn("*No content returned from model.*")
            logger.warning(f"No content returned from model. Full response: {response}")
            return

        # Deal with LLM output
        for part in response.candidates[0].content.parts:
            
            #  LLM requested function calls
            if part.function_call:
                tool_name = part.function_call.name
                response = await self.mcpc.execute_tool(tool_name, part.function_call.args)
                function_response_part = genai.types.Part.from_function_response(
                    name = tool_name,
                    response=response
                )
                resp = genai.types.Content(role="function", parts=[function_response_part])
                self.contents.append(resp)

                self.answer_call() # Recursive call to handle any new model output after tool execution


            # LLM Text output
            elif part.text:
                self.display.markdown(part.text)
                
            else:
                self.display.warn("Unknown part")
                s = json.dumps(response, indent=2)
                self.display.markdown(f"```{s}```")
                break

