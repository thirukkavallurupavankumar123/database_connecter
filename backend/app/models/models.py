import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    connections = relationship("DatabaseConnection", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    query_history = relationship("QueryHistory", back_populates="user", cascade="all, delete-orphan")


class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    db_type = Column(String(50), nullable=False)  # postgresql, mysql, sqlserver, snowflake, bigquery
    host = Column(String(255), nullable=False)
    port = Column(String(10), nullable=True)
    database_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    encrypted_password = Column(Text, nullable=False)  # AES-encrypted
    ssl_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="connections")
    schema_cache = relationship("SchemaCache", back_populates="connection", cascade="all, delete-orphan")


class SchemaCache(Base):
    __tablename__ = "schema_cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    connection_id = Column(String, ForeignKey("database_connections.id"), nullable=False)
    schema_json = Column(Text, nullable=False)  # JSON string of schema metadata
    updated_at = Column(DateTime, default=datetime.utcnow)

    connection = relationship("DatabaseConnection", back_populates="schema_cache")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    connection_id = Column(String, ForeignKey("database_connections.id"), nullable=False)
    natural_language_query = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, success, error
    error_message = Column(Text, nullable=True)
    row_count = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="query_history")
