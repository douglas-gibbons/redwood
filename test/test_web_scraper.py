import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from server.web_scraper import get_webpage_content

@pytest.mark.asyncio
async def test_get_webpage_content():
    url = "https://example.com"
    html_content = "<html><body><h1>Hello World</h1></body></html>"
    expected_markdown = "Hello World\n===========\n\n"

    # Mock httpx.AsyncClient
    mock_response = MagicMock()
    mock_response.text = html_content
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client) as mock_async_client:
        result = await get_webpage_content(url)
        
    assert "Hello World" in result
    mock_client.get.assert_called_once_with(url)
    
    expected_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    mock_async_client.assert_called_once_with(follow_redirects=True, headers=expected_headers)
