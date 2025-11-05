import datetime
from server import mcp

@mcp.tool()
def get_current_date_and_time() -> str:
    """Outputs the current date and time in ISO format"""
    return datetime.datetime.now().isoformat()

