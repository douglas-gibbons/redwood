import database
from typing import Optional
from . import mcp

@mcp.tool()
def get_categories() -> str:
    """Outputs the categories in the database in alphabetical order"""
    categories = database.get_categories()
    return "Categories:\n" + "\n".join(categories) if categories else "No categories found."

@mcp.tool()
def get_records_by_category(category: str) -> str:
    """Outputs the records for a given category"""
    records = database.get_records_by_category(category)
    if not records:
        return f"No records found for category: {category}"
    return "\n".join([f"[{r['id']}] {r['created']} - {r['content']}" for r in records])

@mcp.tool()
def add_record(category: str, content: str) -> str:
    """Adds a new record to the database"""
    new_id = database.add_record(category, content)
    return str(new_id)

@mcp.tool()
def delete_record(record_id: int) -> str:
    """Deletes a record from the database by its id. Returns True if successful, False otherwise."""
    success = database.delete_record(record_id)
    return str(success)

@mcp.tool()
def modify_record(
    record_id: int, category: Optional[str] = None, content: Optional[str] = None
) -> str:
    """
    Modifies a record's category and/or content. Returns True if successful, False otherwise.
    """
    success = database.modify_record(record_id, category, content)
    return str(success)
