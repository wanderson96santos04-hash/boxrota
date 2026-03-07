"""add stock_qty to parts

Revision ID: e97ae8d56054
Revises: add_workshop_slug
Create Date: 2026-03-07 20:58:13.343506
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e97ae8d56054"
down_revision: Union[str, None] = "add_workshop_slug"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "parts",
        sa.Column("stock_qty", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("parts", "stock_qty")