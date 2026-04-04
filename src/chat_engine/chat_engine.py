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

    def set_initial_prompt(self, contents, config):
        # Set initial prompt
        # Gemini only has user and system prompts
        if config.exists("prompt"):
            contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=config.prompt)]))
            contents.append(genai.types.Content(role="model", parts=[genai.types.Part(text="Understood")]))

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

    async def engine(self):
        logger.info("Starting redwood main")
        
        self.display.info("Welcome to Redwood!")
        self.print_help()

        # Load config file
        config = Config(DEFAULT_CONFIG_FILE)

        if not config.exists("model.api_key"):
            raise ValueError("API Key missing from configuration file")

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=config.logging.level,
            filemode='a',
            filename=config.logging.file
        )

        client = genai.Client(api_key=config.model.api_key)

        mcp_servers = []
        for server_config in config.mcp:
            server = mcp_client.dict_to_server(server_config)
            mcp_servers.append(server)
        
        token_storage_config = None
        if config.exists("token_storage.enabled") and config.token_storage.enabled:
            token_storage_config = mcp_client.TokenStorageConfig(
                enabled = config.token_storage.enabled,
                location = os.path.expanduser(config.token_storage.location),
                encryption_key = config.token_storage.encryption_key
            )
        mcpc = mcp_client.MCPClient(servers=mcp_servers, log_file=config.logging.file, token_storage_config=token_storage_config)
        
        # Gemini model name
        model_name = config.model.name
        self.display.markdown(f"Using model: `{model_name}`")

        tools = await mcpc.list_tools()

        # Chat contents
        contents = []

        self.set_initial_prompt(contents, config)

        gemini_config = genai.types.GenerateContentConfig(
            tools = tools,
            automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )
        
        model_calls: int = 0
        ask_user = True

        # logging.getLogger().handlers.clear()
        logger.info("Entering main loop")

        while True:
            
            if ask_user:

                sys.stdout.flush()
                user_input = self.display.input()
                if user_input == "/exit" or user_input == "/x":
                    break
                if user_input == "/tools" or user_input == "/t":
                    self.print_tools(tools)
                    continue
                if user_input == "/conversation" or user_input == "/c":
                    self.print_conversation(contents)
                    continue
                if user_input == "/locate" or user_input == "/l":
                    self.set_location(contents)
                    continue
                if user_input == "/help" or user_input == "/?":
                    self.print_help()
                    continue
                if user_input == "/reset" or user_input == "/r":
                    contents.clear()
                    self.set_initial_prompt(contents, config)
                    self.display.info("Conversation history reset")
                    continue
                
                # Append user output to contents
                contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=user_input)]))
            
            # Safety valve
            if model_calls >= int(config.max_model_calls):
                self.display.warn("Max model calls reached")
                self.display.info("This is a safety valve to catch costly looping. You can increase the limit in the config file if needed.")
                break
            model_calls += 1
            
            # Call LLM
            response = client.models.generate_content(
                model = model_name,
                contents = contents,
                config = gemini_config
            )
            
            # Append LLM output to contents
            contents.append(response.candidates[0].content)

            if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                self.display.warn("*No content returned from model.*")
                logger.warning(f"No content returned from model. Full response: {response}")
                continue

            # Deal with LLM output
            for part in response.candidates[0].content.parts:
                
                #  LLM requested function calls
                if part.function_call:
                    tool_name = part.function_call.name
                    response = await mcpc.execute_tool(tool_name, part.function_call.args)
                    function_response_part = genai.types.Part.from_function_response(
                        name = tool_name,
                        response=response
                    )
                    resp = genai.types.Content(role="function", parts=[function_response_part])
                    contents.append(resp)
                    ask_user = False

                # LLM Text output
                elif part.text:
                    self.display.markdown(part.text)
                    ask_user = True
                else:
                    self.display.warn("Unknown part")
                    s = json.dumps(response, indent=2)
                    self.display.markdown(f"```{s}```")
                    break
                
        logger.info(f"chat contents: {contents}")
