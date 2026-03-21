import unittest
from unittest.mock import patch, MagicMock

import pytest

from config import Config
from agent import ask_subagent

def test_ask_subagent_no_api_key():
    # Mock Config so it returns False for exists("model.api_key")
    with patch("agent.Config") as mock_config_class:
        mock_config = MagicMock()
        mock_config.exists.side_effect = lambda k: False
        mock_config_class.return_value = mock_config
        
        result = ask_subagent("Test prompt")
        assert result == "Error: API Key missing from configuration"

def test_ask_subagent_success():
    # Mock Config and genai.Client
    with patch("agent.Config") as mock_config_class, \
         patch("agent.genai.Client") as mock_client_class:
        
        # Setup mock Config
        mock_config = MagicMock()
        mock_config.exists.side_effect = lambda k: True
        mock_config.model.api_key = "FAKE-KEY"
        mock_config.model.name = "gemini-test"
        mock_config_class.return_value = mock_config
        
        # Setup mock Client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Mock LLM Response"
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        result = ask_subagent("Test prompt")
        
        assert result == "Mock LLM Response"
        mock_client_class.assert_called_once_with(api_key="FAKE-KEY")
        mock_client.models.generate_content.assert_called_once_with(
            model="gemini-test",
            contents="Test prompt"
        )
