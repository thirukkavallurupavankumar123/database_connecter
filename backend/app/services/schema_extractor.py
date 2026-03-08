import json
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from typing import Any


def extract_schema(engine: Engine) -> list[dict[str, Any]]:
    """Extract table/column metadata from a client database.
    Returns a list of tables with their columns and types."""
    inspector = inspect(engine)
    tables = []

    for table_name in inspector.get_table_names():
        columns = []
        for col in inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
            })

        pk = inspector.get_pk_constraint(table_name)
        primary_keys = pk.get("constrained_columns", []) if pk else []

        tables.append({
            "table_name": table_name,
            "columns": columns,
            "primary_keys": primary_keys,
            "row_estimate": _estimate_row_count(engine, table_name),
        })

    return tables


def _estimate_row_count(engine: Engine, table_name: str) -> int:
    """Get an approximate row count for a table (fast, not exact)."""
    try:
        with engine.connect() as conn:
            # Use a parameterized identifier approach safely
            # table_name comes from inspector.get_table_names() which is trusted
            result = conn.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            )
            return result.scalar() or 0
    except Exception:
        return -1


def schema_to_prompt_context(tables: list[dict]) -> str:
    """Convert schema metadata into a text block for AI prompt context."""
    lines = ["DATABASE SCHEMA:", ""]
    for table in tables:
        col_defs = ", ".join(
            f"{c['name']} ({c['type']})" for c in table["columns"]
        )
        pk_info = f"  Primary Keys: {', '.join(table['primary_keys'])}" if table["primary_keys"] else ""
        lines.append(f"Table: {table['table_name']}")
        lines.append(f"  Columns: {col_defs}")
        if pk_info:
            lines.append(pk_info)
        lines.append(f"  Approx rows: {table['row_estimate']}")
        lines.append("")

    return "\n".join(lines)
