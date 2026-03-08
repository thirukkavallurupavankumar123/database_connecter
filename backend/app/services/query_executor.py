from sqlalchemy import text
from sqlalchemy.engine import Engine
from app.config import get_settings


def execute_readonly_query(engine: Engine, sql: str) -> tuple[list[str], list[dict]]:
    """Execute a validated read-only SQL query and return (columns, rows).
    Enforces row limit and query timeout."""
    settings = get_settings()
    max_rows = settings.MAX_ROWS
    timeout = settings.QUERY_TIMEOUT_SECONDS

    with engine.connect() as conn:
        # Set statement timeout where supported
        try:
            _set_timeout(conn, engine.dialect.name, timeout)
        except Exception:
            pass  # Not all DBs support statement-level timeouts

        result = conn.execute(text(sql))
        columns = list(result.keys())

        rows = []
        for i, row in enumerate(result):
            if i >= max_rows:
                break
            rows.append(dict(zip(columns, row)))

        return columns, rows


def _set_timeout(conn, dialect_name: str, timeout_sec: int):
    """Set a query timeout for supported databases."""
    timeout_ms = timeout_sec * 1000
    if dialect_name == "postgresql":
        conn.execute(text(f"SET statement_timeout = {timeout_ms}"))
    elif dialect_name == "mysql":
        conn.execute(text(f"SET max_execution_time = {timeout_ms}"))
