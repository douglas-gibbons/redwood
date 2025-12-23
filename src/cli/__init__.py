import asyncio
import os
from google import genai
from rich.console import Console
from rich.markdown import Markdown
import mcp_client
import pprint
import logging
from config import Config
import sys
import readline # needed for input() to write to stdout instead of stderr

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.config/redwood.yaml")

logging.getLogger().handlers.clear()
logger = logging.getLogger(__name__)

def print_tools(tools):
    console = Console()
    console.print("[bold]Available Tools:[/bold]")
    tools_by_server = {}
    for tool in tools:
        server_name, tool_name = mcp_client.get_tool_name(tool.name)
        if server_name not in tools_by_server:
            tools_by_server[server_name] = []
        tools_by_server[server_name].append((tool_name, tool))
    
    for server_name, server_tools in tools_by_server.items():
        console.print(f"\n[bold magenta]Server: {server_name}[/bold magenta]")
        for tool_name, tool in server_tools:
            console.print(f"  [bold cyan]{tool_name}[/bold cyan]")
            if tool.description:
                console.print(f"    {tool.description}")
            if tool.inputSchema:
                console.print(f"    Args: {tool.inputSchema}")

def print_conversation(contents):
    console = Console()
    console.print("[bold]Conversation History:[/bold]")
    console.print(contents)

async def main():
    logger.info("Starting redwood main")
    
    console = Console()
    console.print("\n[bold green]Welcome to Redwood![/bold green]\n")
    console.print("You can interact with the AI model and use various tools via MCP servers.")
    console.print("Tools: Type '/tools' to list available tools.")
    console.print("Conversation: Type '/conversation' to show conversation history.")
    console.print("Exit: Type '/exit' to quit.\n")

    # Load config file
    config = Config(DEFAULT_CONFIG_FILE)

    if not config.exists("model.api_key"):
        raise("API Key missing from configuration file")

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
    
    mcpc = mcp_client.MCPClient(servers=mcp_servers, log_file=config.logging.file)
    
    # Gemini model name
    model_name = config.model.name
    print(f"Using model: {model_name}")

    tools = await mcpc.list_tools()

    # Chat contents
    contents = []

    # Set initial prompt
    # Gemini only has user and system prompts
    if config.exists("prompt"):
        prompt = config.prompt
        contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=prompt)]))
        contents.append(genai.types.Content(role="model", parts=[genai.types.Part(text="Understood")]))

    gemini_config = genai.types.GenerateContentConfig(
        tools = tools,
        automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )
    
    model_calls = 0
    ask_user = True

    # logging.getLogger().handlers.clear()
    logger.info("Entering main loop")

    while True:
        
        if ask_user:

            sys.stdout.flush()
            user_input = input(">> ")
            if user_input == "/exit":
                break
            if user_input == "/tools":
                print_tools(tools)
                continue
            if user_input == "/conversation":
                print_conversation(contents)
                continue
            
            # Append user output to contents
            contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=user_input)]))
        
        # Safety valve
        if model_calls >= config.max_model_calls:
            console.print("[bold red]Max model calls reached.[/bold red]")
            console.print("This is a safety valve to catch costly looping. You can increase the limit in the config file if needed.")
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
                console.print(Markdown(part.text))
                ask_user = True
            else:
                print("Unknown part")
                pprint.pprint(response, depth=20)
                break
            
    logger.info(f"chat contents: {contents}")

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
