"""Make database functions available at the package level."""
from .database import (
    add_record,
    get_records_by_category,
    get_categories,
    delete_record,
    modify_record,
    get_db_connection,
)

database.init_db()