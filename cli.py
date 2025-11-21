import asyncio
import os
from google import genai
import yaml
from rich.console import Console
from rich.markdown import Markdown
import mcp_client
import pprint
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    console = Console()

    # Get API key from environment variable
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Load config file
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    mcpc = mcp_client.MCPClient("config.yaml")
    
    # Gemini model name
    model_name = config["model"]["name"]
    print(f"Using model: {model_name}")

    tools = await mcpc.list_tools()

    # Chat contents
    contents = []

    # Set initial prompt
    # Gemini only has user and system prompts
    if "prompt" in config:
        prompt = config["prompt"]
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
        if model_calls >= config.get("max_model_calls", 0):
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
