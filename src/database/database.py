import sqlite3
from datetime import datetime
from typing import Optional

DB_FILE = "mcp_data.db"


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database and creates the 'records' table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL
        );
    """
    )
    conn.commit()
    conn.close()


def add_record(category: str, content: str) -> int:
    """
    Adds a new record to the database.
    Returns the id of the newly inserted record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    created_time = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO records (created, category, content) VALUES (?, ?, ?)",
        (created_time, category, content),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_records_by_category(category: str) -> list[dict]:
    """Retrieves all records for a given category, ordered by creation date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, created, category, content FROM records WHERE category = ? ORDER BY created DESC",
        (category,),
    )
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records


def get_categories() -> list[str]:
    """Retrieves a list of all unique categories from the records table, sorted alphabetically."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM records ORDER BY category ASC")
    # The row_factory makes each row dict-like, so we can access 'category' by name.
    categories = [row["category"] for row in cursor.fetchall()]
    conn.close()
    return categories


def delete_record(record_id: int) -> bool:
    """
    Deletes a record from the database by its id.
    Returns True if a record was deleted, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def modify_record(
    record_id: int, category: Optional[str] = None, content: Optional[str] = None
) -> bool:
    """
    Modifies a record's category and/or content.
    Returns True if the record was updated, False otherwise.
    """
    if category is None and content is None:
        return False  # Nothing to update

    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    params = []
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if content is not None:
        updates.append("content = ?")
        params.append(content)

    query = f"UPDATE records SET {', '.join(updates)} WHERE id = ?"
    params.append(record_id)
    cursor.execute(query, tuple(params))

    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()
    return updated_rows > 0