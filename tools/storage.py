from server import mcp
import database
from typing import Optional

@mcp.tool()
def get_categories() -> list[str]:
    """Outputs the categories in the database in alphabetical order"""
    return database.get_categories()

@mcp.tool()
def get_records_by_category(category: str) -> list[dict]:
    """Outputs the records for a given category"""
    return database.get_records_by_category(category)

@mcp.tool()
def add_record(category: str, content: str) -> int:
    """Adds a new record to the database"""
    return database.add_record(category, content)

@mcp.tool()
def delete_record(record_id: int) -> bool:
    """Deletes a record from the database by its id. Returns True if successful, False otherwise."""
    return database.delete_record(record_id)

@mcp.tool()
def modify_record(
    record_id: int, category: Optional[str] = None, content: Optional[str] = None
) -> bool:
    """
    Modifies a record's category and/or content. Returns True if successful, False otherwise.
    """
    return database.modify_record(record_id, category, content)
