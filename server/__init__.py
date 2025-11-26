from mcp.server.fastmcp import FastMCP
import logging

logging.getLogger().handlers.clear()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
)

mcp = FastMCP(name = "redwood")
