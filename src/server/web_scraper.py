import httpx
from markdownify import markdownify as md
from . import mcp

@mcp.tool()
async def get_webpage_content(url: str) -> str:
    """
    Retrieves the content of a webpage and returns it as markdown.
    
    Args:
        url: The URL of the webpage to retrieve.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        html_content = response.text
        
    markdown_content = md(html_content)
    return markdown_content
