from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
mcp = FastMCP(name = "redwood")
