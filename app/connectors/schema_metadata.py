import sqlite3

from app.core.config import get_settings

BUSINESS_TABLES = ["dim_customer", "dim_product", "dim_date", "fact_sales"]


def _connect_db() -> sqlite3.Connection:
    settings = get_settings()
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_tables() -> list[str]:
    with _connect_db() as conn:
        rows = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN (?, ?, ?, ?)
            ORDER BY CASE name
                WHEN 'dim_customer' THEN 1
                WHEN 'dim_product' THEN 2
                WHEN 'dim_date' THEN 3
                WHEN 'fact_sales' THEN 4
                ELSE 99
            END
            """,
            BUSINESS_TABLES,
        ).fetchall()
    return [row["name"] for row in rows]


def get_columns(table_name: str) -> list[dict]:
    with _connect_db() as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [
        {
            "name": row["name"],
            "type": row["type"],
            "not_null": bool(row["notnull"]),
            "default_value": row["dflt_value"],
            "primary_key_position": row["pk"],
        }
        for row in rows
    ]


def get_primary_key(table_name: str) -> list[str]:
    columns = get_columns(table_name)
    primary_key_columns = [col for col in columns if col["primary_key_position"] > 0]
    primary_key_columns.sort(key=lambda col: col["primary_key_position"])
    return [col["name"] for col in primary_key_columns]


def get_foreign_keys(table_name: str) -> list[dict]:
    with _connect_db() as conn:
        rows = conn.execute(f"PRAGMA foreign_key_list({table_name})").fetchall()
    return [
        {
            "from": row["from"],
            "to_table": row["table"],
            "to_column": row["to"],
        }
        for row in rows
    ]


def get_relations() -> list[dict]:
    relations = []
    for table_name in get_tables():
        for foreign_key in get_foreign_keys(table_name):
            relations.append(
                {
                    "from_table": table_name,
                    "from_column": foreign_key["from"],
                    "to_table": foreign_key["to_table"],
                    "to_column": foreign_key["to_column"],
                }
            )
    return relations


def get_schema_metadata() -> dict:
    metadata = {}
    for table_name in get_tables():
        metadata[table_name] = {
            "columns": get_columns(table_name),
            "primary_key": get_primary_key(table_name),
            "foreign_keys": get_foreign_keys(table_name),
        }
    return metadata


def format_schema_for_llm() -> str:
    metadata = get_schema_metadata()
    lines = []

    for table_name in get_tables():
        lines.append(f"TABLE {table_name}")
        primary_key = set(metadata[table_name]["primary_key"])
        foreign_keys = {
            fk["from"]: f"{fk['to_table']}.{fk['to_column']}"
            for fk in metadata[table_name]["foreign_keys"]
        }

        for column in metadata[table_name]["columns"]:
            definition = f"- {column['name']} {column['type']}"
            if column["name"] in primary_key:
                definition += " PRIMARY KEY"
            if column["name"] in foreign_keys:
                definition += f" -> {foreign_keys[column['name']]}"
            lines.append(definition)
        lines.append("")

    lines.append("RELATIONS")
    for relation in get_relations():
        lines.append(
            f"{relation['from_table']}.{relation['from_column']} -> "
            f"{relation['to_table']}.{relation['to_column']}"
        )

    return "\n".join(lines)
