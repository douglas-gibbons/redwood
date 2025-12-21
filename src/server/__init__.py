from mcp.server.fastmcp import FastMCP
import logging

logging.getLogger().handlers.clear()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
)

mcp = FastMCP(name = "redwood")

# Import tools to register them
from . import command
from . import mcptime
from . import storage
from . import web_scraper

def run():
    mcp.run()

if __name__ == "__main__":
    run()
