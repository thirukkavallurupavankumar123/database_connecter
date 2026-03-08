from typing import Literal, Optional
from pydantic import BaseModel
from datetime import datetime


# --- Organization ---
class OrganizationCreate(BaseModel):
    name: str
    password: str


class OrganizationResponse(BaseModel):
    id: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- User ---
class UserCreate(BaseModel):
    email: str
    name: str
    organization_id: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    organization_id: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Auth ---
class SignupRequest(BaseModel):
    email: str
    name: str
    password: str
    organization_name: Optional[str] = None       # create new org
    organization_password: Optional[str] = None   # org password (required for both create & join)
    organization_id: Optional[str] = None          # join existing org


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    user_id: str
    user_name: str
    email: str
    organization_id: str
    organization_name: str


# --- Database Connection ---
class DatabaseConnectionCreate(BaseModel):
    organization_id: str
    user_id: str
    name: str
    db_type: Literal["postgresql", "mysql", "sqlserver"]
    host: str
    port: Optional[str] = None
    database_name: str
    username: str
    password: str  # plaintext — will be encrypted before storage
    ssl_enabled: bool = True


class DatabaseConnectionResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    db_type: str
    host: str
    port: Optional[str]
    database_name: str
    username: str
    ssl_enabled: bool
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DatabaseConnectionTest(BaseModel):
    db_type: Literal["postgresql", "mysql", "sqlserver"]
    host: str
    port: Optional[str] = None
    database_name: str
    username: str
    password: str
    ssl_enabled: bool = True


# --- Connect Session ---
class ConnectRequest(BaseModel):
    user_id: str


class ConnectionInfo(BaseModel):
    id: str
    name: str
    db_type: str
    host: str
    database_name: str

    model_config = {"from_attributes": True}


class ConnectResponse(BaseModel):
    user_id: str
    user_name: str
    organization_id: str
    organization_name: str
    connections: list[ConnectionInfo]


# --- Query ---
class QueryRequest(BaseModel):
    connection_id: str
    user_id: str
    natural_language_query: str


class QueryResponse(BaseModel):
    query_id: str
    natural_language_query: str
    generated_sql: str
    columns: list[str]
    data: list[dict]
    row_count: int
    statistics: Optional[dict] = None
    ai_summary: Optional[str] = None
    ai_insights: Optional[list[str]] = None


class QueryHistoryResponse(BaseModel):
    id: str
    natural_language_query: str
    generated_sql: Optional[str]
    status: str
    error_message: Optional[str]
    row_count: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Schema ---
class SchemaResponse(BaseModel):
    connection_id: str
    tables: list[dict]


# --- Report ---
class ReportRequest(BaseModel):
    connection_id: str
    user_id: str
    natural_language_query: str
    format: Literal["csv", "excel", "json", "pdf"]


# --- Generic ---
class MessageResponse(BaseModel):
    message: str
    success: bool = True
