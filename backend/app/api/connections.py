import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import DatabaseConnection, SchemaCache, Organization
from app.schemas.schemas import (
    DatabaseConnectionCreate, DatabaseConnectionResponse,
    DatabaseConnectionTest, SchemaResponse, MessageResponse,
)
from app.services.encryption import encrypt_password
from app.services.database_connector import get_client_engine, test_connection
from app.services.schema_extractor import extract_schema

router = APIRouter(prefix="/api/connections", tags=["Database Connections"])


@router.post("/test", response_model=MessageResponse)
def test_db_connection(payload: DatabaseConnectionTest):
    """Test a database connection before saving."""
    success = test_connection(
        db_type=payload.db_type, host=payload.host, port=payload.port,
        database_name=payload.database_name, username=payload.username,
        password=payload.password, ssl_enabled=payload.ssl_enabled,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Connection failed. Check credentials and network.")
    return MessageResponse(message="Connection successful!", success=True)


@router.post("/", response_model=DatabaseConnectionResponse)
def create_connection(payload: DatabaseConnectionCreate, db: Session = Depends(get_db)):
    """Save a new database connection (credentials are encrypted)."""
    org = db.query(Organization).filter(Organization.id == payload.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Test connection first
    success = test_connection(
        db_type=payload.db_type, host=payload.host, port=payload.port,
        database_name=payload.database_name, username=payload.username,
        password=payload.password, ssl_enabled=payload.ssl_enabled,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Cannot save — connection test failed.")

    encrypted_pw = encrypt_password(payload.password)
    conn = DatabaseConnection(
        organization_id=payload.organization_id,
        name=payload.name,
        db_type=payload.db_type,
        host=payload.host,
        port=payload.port,
        database_name=payload.database_name,
        username=payload.username,
        encrypted_password=encrypted_pw,
        ssl_enabled=payload.ssl_enabled,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)

    # Extract and cache schema
    _refresh_schema_cache(conn, db)

    return conn


@router.get("/org/{org_id}", response_model=list[DatabaseConnectionResponse])
def list_connections(org_id: str, db: Session = Depends(get_db)):
    """List all database connections for an organization."""
    return db.query(DatabaseConnection).filter(
        DatabaseConnection.organization_id == org_id
    ).all()


@router.get("/{conn_id}", response_model=DatabaseConnectionResponse)
def get_connection(conn_id: str, db: Session = Depends(get_db)):
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return conn


@router.delete("/{conn_id}", response_model=MessageResponse)
def delete_connection(conn_id: str, db: Session = Depends(get_db)):
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    db.delete(conn)
    db.commit()
    return MessageResponse(message="Connection deleted")


@router.get("/{conn_id}/schema", response_model=SchemaResponse)
def get_schema(conn_id: str, db: Session = Depends(get_db)):
    """Get cached schema for a database connection."""
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    cache = db.query(SchemaCache).filter(SchemaCache.connection_id == conn_id).first()
    if not cache:
        cache = _refresh_schema_cache(conn, db)

    tables = json.loads(cache.schema_json)
    return SchemaResponse(connection_id=conn_id, tables=tables)


@router.post("/{conn_id}/schema/refresh", response_model=SchemaResponse)
def refresh_schema(conn_id: str, db: Session = Depends(get_db)):
    """Force-refresh the cached schema for a connection."""
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

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
