"""Add label, tags, is_default to database_connections

Revision ID: 002_add_routing
Revises: 001_initial
Create Date: 2026-03-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_add_routing"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("database_connections", sa.Column("label", sa.String(length=255), nullable=True))
    op.add_column("database_connections", sa.Column("tags", sa.Text(), nullable=True))
    op.add_column("database_connections", sa.Column("is_default", sa.Boolean(), nullable=True, server_default=sa.text("FALSE")))


def downgrade() -> None:
    op.drop_column("database_connections", "is_default")
    op.drop_column("database_connections", "tags")
    op.drop_column("database_connections", "label")
