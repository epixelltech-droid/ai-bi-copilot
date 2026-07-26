import sqlite3
from app.core.config import get_settings
from app.tools.sql_guard import validate_readonly_sql


def execute_demo_sql(query: str) -> list[dict]:
    s = get_settings()
    query = validate_readonly_sql(query)
    conn = sqlite3.connect(s.sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(query)
        return [dict(r) for r in cur.fetchmany(s.max_rows)]
    finally:
        conn.close()
