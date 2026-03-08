from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from typing import Optional
from urllib.parse import quote_plus
from app.services.encryption import decrypt_password


def build_connection_url(db_type: str, host: str, port: Optional[str],
                         database_name: str, username: str,
                         encrypted_password: str, ssl_enabled: bool) -> str:
    """Build a SQLAlchemy connection URL from stored (encrypted) connection params."""
    password = decrypt_password(encrypted_password)
    # URL-encode password to handle special characters like @, /, :, etc.
    password_encoded = quote_plus(password)
    username_encoded = quote_plus(username)

    drivers = {
        "postgresql": "postgresql+psycopg2",
        "mysql": "mysql+pymysql",
        "sqlserver": "mssql+pyodbc",
    }

    driver = drivers.get(db_type)
    if not driver:
        raise ValueError(f"Unsupported database type: {db_type}")

    port_part = f":{port}" if port else ""

    if db_type == "sqlserver":
        return (
            f"{driver}://{username_encoded}:{password_encoded}@{host}{port_part}/{database_name}"
            f"?driver=ODBC+Driver+17+for+SQL+Server"
        )

    return f"{driver}://{username_encoded}:{password_encoded}@{host}{port_part}/{database_name}"


def get_client_engine(db_type: str, host: str, port: Optional[str],
                      database_name: str, username: str,
                      encrypted_password: str, ssl_enabled: bool) -> Engine:
    """Create a read-only SQLAlchemy engine for a client database."""
    url = build_connection_url(db_type, host, port, database_name,
                               username, encrypted_password, ssl_enabled)

    connect_args = {}
    if ssl_enabled:
        if db_type == "postgresql":
            connect_args["sslmode"] = "require"
        elif db_type == "mysql":
            # PyMySQL SSL config
            import ssl
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ssl_ctx

    return create_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=3,
    )


def test_connection(db_type: str, host: str, port: Optional[str],
                    database_name: str, username: str,
                    password: str, ssl_enabled: bool) -> tuple[bool, str]:
    """Test a database connection using raw (unencrypted) credentials.
    Used before saving a new connection. Returns (success, error_message)."""
    from app.services.encryption import encrypt_password
    encrypted = encrypt_password(password)
    engine = get_client_engine(db_type, host, port, database_name,
                               username, encrypted, ssl_enabled)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, ""
    except Exception as e:
        return False, str(e)
    finally:
        engine.dispose()
