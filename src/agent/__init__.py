from mcp.server.fastmcp import FastMCP
from google import genai
from config import Config
import logging

logging.getLogger().handlers.clear()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
)

mcp = FastMCP(name="subagent")

@mcp.tool()
def ask_subagent(prompt: str) -> str:
    """
    Ask a sub-agent to fulfill a prompt or answer a question.
    The sub-agent is an LLM that can help with complex reasoning, writing, or analysis.
    
    Args:
        prompt: The prompt, task, or question to send to the sub-agent.
    """
    config = Config()
    if not config.exists("model.api_key"):
        return "Error: API Key missing from configuration"
    
    client = genai.Client(api_key=config.model.api_key)
    
    # Use config model name or default to flash
    if config.exists("model.name"):
        model_name = config.model.name
    else:
        model_name = "gemini-2.5-flash"
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error executing sub-agent query: {str(e)}"

def run():
    mcp.run()

if __name__ == "__main__":
    run()
