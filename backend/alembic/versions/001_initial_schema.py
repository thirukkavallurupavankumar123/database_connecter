"""Initial schema - all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-03-08

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime()),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("organization_id", sa.String(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime()),
    )

    # Database connections
    op.create_table(
        "database_connections",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("organization_id", sa.String(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("db_type", sa.String(50), nullable=False),
        sa.Column("host", sa.String(255), nullable=False),
        sa.Column("port", sa.String(10), nullable=True),
        sa.Column("database_name", sa.String(255), nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("encrypted_password", sa.Text(), nullable=False),
        sa.Column("ssl_enabled", sa.Boolean(), default=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
    )

    # Schema cache
    op.create_table(
        "schema_cache",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("connection_id", sa.String(), sa.ForeignKey("database_connections.id"), nullable=False),
        sa.Column("schema_json", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime()),
    )

    # Query history
    op.create_table(
        "query_history",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("connection_id", sa.String(), sa.ForeignKey("database_connections.id"), nullable=False),
        sa.Column("natural_language_query", sa.Text(), nullable=False),
        sa.Column("generated_sql", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("row_count", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table("query_history")
    op.drop_table("schema_cache")
    op.drop_table("database_connections")
    op.drop_table("users")
    op.drop_table("organizations")
