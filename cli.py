import asyncio
import os
from google import genai
import yaml
from rich.console import Console
from rich.markdown import Markdown
import mcp_client
import pprint
import logging
from config import Config

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.config/redwood.yaml")

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    console = Console()

    # Load config file
    config = Config(DEFAULT_CONFIG_FILE)

    if not config.exists("model.api_key"):
        raise("API Key missing from configuration file")

    client = genai.Client(api_key=config.model.api_key)


    mcpc = mcp_client.MCPClient(config.mcp)
    
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

    while True:
        
        if ask_user:
            user_input = input(">> ")
            if user_input == "exit" or user_input == "/exit":
                break
            # Append user output to contents
            contents.append(genai.types.Content(role="user", parts=[genai.types.Part(text=user_input)]))
        
        # Safety valve
        if model_calls >= config.max_model_calls:
            print("Max model calls reached. This is a safety valve to catch costly looping")
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
                    response=response.structured_content
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
            
    pprint.pprint(contents)


if __name__ == "__main__":
    asyncio.run(main())
