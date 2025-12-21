import subprocess
from . import mcp

@mcp.tool()
def run_command(command: str) -> str:
    """Run a command and return its output as a string"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        return f"Error: {result.stderr}"
