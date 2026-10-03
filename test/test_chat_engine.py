import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from chat_engine.chat_engine import ChatEngine
from chat_engine.display_interface import DisplayInterface
import mcp_client

class MockDisplay(DisplayInterface):
    async def info(self, message: str):
        pass

    async def warn(self, message: str):
        pass

    async def error(self, message: str):
        pass

    async def markdown(self, prompt: str) -> str:
        return prompt

    async def quit(self, message: str = None):
        pass

    async def ask_yes_no(self, question: str) -> bool:
        return True

    async def ask_question(self, question: str) -> str:
        return "test"

    async def tool_log(self, message: str):
        pass

@pytest.fixture
def mock_chat_engine():
    display = MockDisplay()
    display.info = AsyncMock()
    display.warn = AsyncMock()
    display.error = AsyncMock()
    display.markdown = AsyncMock()
    display.quit = AsyncMock()
    display.ask_yes_no = AsyncMock(return_value=True)
    display.ask_question = AsyncMock(return_value="test")
    display.tool_log = AsyncMock()

    with patch("chat_engine.chat_engine.Config") as mock_config_class:
        mock_config = MagicMock()
        mock_config.model.name = "gemini-test"
        mock_config.logging.level = "INFO"
        mock_config.logging.file = None
        mock_config.max_model_calls = 20
        mock_config_class.return_value = mock_config
        engine = ChatEngine(display)
        return engine

@pytest.mark.asyncio
async def test_yolo_command_toggle(mock_chat_engine):
    engine = mock_chat_engine
    engine.mcpc = MagicMock()
    engine.mcpc.yolo_mode = False

    # Default is off
    assert engine.yolo_mode is False

    # /yolo enables
    result = await engine._handle_command("/yolo")
    assert result is True
    assert engine.yolo_mode is True
    assert engine.mcpc.yolo_mode is True
    engine.display.info.assert_called_with("YOLO mode enabled. Tool execution prompts are disabled.")

    # /yolo off disables
    result = await engine._handle_command("/yolo off")
    assert result is True
    assert engine.yolo_mode is False
    assert engine.mcpc.yolo_mode is False
    engine.display.info.assert_called_with("YOLO mode disabled. Tool execution prompts are enabled.")

    # /yolo on enables
    result = await engine._handle_command("/yolo on")
    assert result is True
    assert engine.yolo_mode is True
    assert engine.mcpc.yolo_mode is True

    # /yolo invalid option warns
    result = await engine._handle_command("/yolo invalid")
    assert result is True
    engine.display.warn.assert_called_with("Invalid option for /yolo. Usage: '/yolo', '/yolo on', or '/yolo off'.")

@pytest.mark.asyncio
async def test_invalid_command_warning(mock_chat_engine):
    engine = mock_chat_engine
    
    # Test unknown command
    result = await engine._handle_command("/maybe")
    assert result is False
    engine.display.warn.assert_called_with("Unknown command: '/maybe'. Type '/help' for a list of available commands.")

    # Test bare slash
    result = await engine._handle_command("/")
    assert result is False
    engine.display.warn.assert_called_with("Unknown command: '/'. Type '/help' for a list of available commands.")

@pytest.mark.asyncio
async def test_answer_call_intercepts_slash_command(mock_chat_engine):
    engine = mock_chat_engine
    engine.gclient = MagicMock()
    
    # Send unknown slash command
    await engine.answer_call("/maybe")
    
    # LLM should not be called
    engine.display.warn.assert_called_with("Unknown command: '/maybe'. Type '/help' for a list of available commands.")
    assert len(engine.contents) == 0

@pytest.mark.asyncio
async def test_mcp_client_yolo_mode_bypasses_prompt():
    display = MockDisplay()
    display.ask_yes_no = AsyncMock(return_value=True)

    server = mcp_client.Server(
        name="testserver",
        ask=True,
        command=None,
        args=[],
        env={},
        url=None,
        headers={}
    )
    client = mcp_client.MCPClient(display=display, servers=[server], yolo_mode=False)

    # When yolo_mode is False and ask is True, ask_yes_no is called
    can_exec = await client.can_execute_tool("testserver", "test_tool", {})
    assert can_exec is True
    assert display.ask_yes_no.call_count == 1

    # When yolo_mode is True, ask_yes_no is NOT called
    client.yolo_mode = True
    display.ask_yes_no.reset_mock()
    can_exec = await client.can_execute_tool("testserver", "test_tool", {})
    assert can_exec is True
    assert display.ask_yes_no.call_count == 0
