import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import DatabaseConnection, SchemaCache, Organization, User
from app.schemas.schemas import (
    DatabaseConnectionCreate, DatabaseConnectionResponse,
    DatabaseConnectionTest, SchemaResponse, MessageResponse,
)
from app.services.encryption import encrypt_password
from app.services.database_connector import get_client_engine, test_connection
from app.services.schema_extractor import extract_schema

router = APIRouter(prefix="/api/connections", tags=["Database Connections"])


def _get_verified_user(user_id: str, db: Session) -> User:
    """Load user and verify they exist and are active."""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or inactive user")
    return user


def _verify_conn_ownership(conn: DatabaseConnection, user: User):
    """Verify a connection belongs to the user's organization."""
    if conn.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied — connection belongs to another organization")


@router.post("/test", response_model=MessageResponse)
def test_db_connection(payload: DatabaseConnectionTest):
    """Test a database connection before saving."""
    success, error = test_connection(
        db_type=payload.db_type, host=payload.host, port=payload.port,
        database_name=payload.database_name, username=payload.username,
        password=payload.password, ssl_enabled=payload.ssl_enabled,
    )
    if not success:
        # Truncate long error messages
        err_msg = error[:200] if error else "Unknown error"
        raise HTTPException(status_code=400, detail=f"Connection failed: {err_msg}")
    return MessageResponse(message="Connection successful!", success=True)


@router.post("/", response_model=DatabaseConnectionResponse)
def create_connection(payload: DatabaseConnectionCreate, db: Session = Depends(get_db)):
    """Save a new database connection (credentials are encrypted)."""
    # Verify the requesting user belongs to the target org
    user = _get_verified_user(payload.user_id, db)
    if user.organization_id != payload.organization_id:
        raise HTTPException(status_code=403, detail="Cannot create connection in another organization")

    org = db.query(Organization).filter(Organization.id == payload.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Test connection first
    success, error = test_connection(
        db_type=payload.db_type, host=payload.host, port=payload.port,
        database_name=payload.database_name, username=payload.username,
        password=payload.password, ssl_enabled=payload.ssl_enabled,
    )
    if not success:
        err_msg = error[:200] if error else "Unknown error"
        raise HTTPException(status_code=400, detail=f"Cannot save — connection test failed: {err_msg}")

    encrypted_pw = encrypt_password(payload.password)
    # If marking as default, unset previous defaults for this org
    if payload.is_default:
        db.query(DatabaseConnection).filter(
            DatabaseConnection.organization_id == payload.organization_id
        ).update({DatabaseConnection.is_default: False})

    conn = DatabaseConnection(
        organization_id=payload.organization_id,
        name=payload.name,
        label=payload.label,
        tags=payload.tags,
        db_type=payload.db_type,
        host=payload.host,
        port=payload.port,
        database_name=payload.database_name,
        username=payload.username,
        encrypted_password=encrypted_pw,
        ssl_enabled=payload.ssl_enabled,
        is_default=payload.is_default,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)

    # Extract and cache schema
    _refresh_schema_cache(conn, db)

    return conn


@router.get("/org/{org_id}", response_model=list[DatabaseConnectionResponse])
def list_connections(org_id: str, user_id: str = Query(...), db: Session = Depends(get_db)):
    """List all database connections for an organization."""
    user = _get_verified_user(user_id, db)
    if user.organization_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied — not your organization")
    return db.query(DatabaseConnection).filter(
        DatabaseConnection.organization_id == org_id
    ).all()


@router.get("/{conn_id}", response_model=DatabaseConnectionResponse)
def get_connection(conn_id: str, user_id: str = Query(...), db: Session = Depends(get_db)):
    user = _get_verified_user(user_id, db)
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    _verify_conn_ownership(conn, user)
    return conn


@router.delete("/{conn_id}", response_model=MessageResponse)
def delete_connection(conn_id: str, user_id: str = Query(...), db: Session = Depends(get_db)):
    user = _get_verified_user(user_id, db)
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    _verify_conn_ownership(conn, user)
    db.delete(conn)
    db.commit()
    return MessageResponse(message="Connection deleted")


@router.get("/{conn_id}/schema", response_model=SchemaResponse)
def get_schema(conn_id: str, user_id: str = Query(...), db: Session = Depends(get_db)):
    """Get cached schema for a database connection."""
    user = _get_verified_user(user_id, db)
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    _verify_conn_ownership(conn, user)

    cache = db.query(SchemaCache).filter(SchemaCache.connection_id == conn_id).first()
    if not cache:
        cache = _refresh_schema_cache(conn, db)

    tables = json.loads(cache.schema_json)
    return SchemaResponse(connection_id=conn_id, tables=tables)


@router.post("/{conn_id}/schema/refresh", response_model=SchemaResponse)
def refresh_schema(conn_id: str, user_id: str = Query(...), db: Session = Depends(get_db)):
    """Force-refresh the cached schema for a connection."""
    user = _get_verified_user(user_id, db)
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    _verify_conn_ownership(conn, user)

    cache = _refresh_schema_cache(conn, db)
    tables = json.loads(cache.schema_json)
    return SchemaResponse(connection_id=conn_id, tables=tables)


def _refresh_schema_cache(conn: DatabaseConnection, db: Session) -> SchemaCache:
    """Extract schema from client DB and update cache."""
    engine = get_client_engine(
        db_type=conn.db_type, host=conn.host, port=conn.port,
        database_name=conn.database_name, username=conn.username,
        encrypted_password=conn.encrypted_password, ssl_enabled=conn.ssl_enabled,
    )
    try:
        tables = extract_schema(engine)
    finally:
        engine.dispose()

    # Upsert cache
    cache = db.query(SchemaCache).filter(SchemaCache.connection_id == conn.id).first()
    if cache:
        cache.schema_json = json.dumps(tables, default=str)
        cache.updated_at = datetime.utcnow()
    else:
        cache = SchemaCache(
            connection_id=conn.id,
            schema_json=json.dumps(tables, default=str),
        )
        db.add(cache)

    db.commit()
    db.refresh(cache)
    return cache
