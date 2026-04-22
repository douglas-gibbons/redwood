from pydantic import BaseModel, Field, RootModel
from typing import Dict, Any, List
import logging
import re

logging.getLogger().handlers.clear()
logger = logging.getLogger(__name__)

class ToolSchema(BaseModel):
    """Sanitizes the JSON Schema for tool arguments."""
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)

class MCPTool(BaseModel):
    """The sanitized version of an MCP tool."""
    model_config = {"from_attributes": True}
    name: str
    description: str | None = "No description provided."
    inputSchema: ToolSchema  # This forces the nested validation

def sanitize_name(name):
    return re.sub(r"[^a-zA-Z0-9]", "", name)

def sanitize_tools(tools):
    sanitized_tools = []
    for tool in tools:
        try:
            clean_tool = MCPTool.model_validate(tool)
            sanitized_tools.append(clean_tool)
        except Exception as e:
            logger.error(f"Error sanitizing tool {tool.name}: {e}")
    return sanitized_tools
