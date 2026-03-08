"""add vehicle type to parts

Revision ID: 2cfbc4a27b3a
Revises: 
Create Date: 2026-03-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2cfbc4a27b3a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "parts",
        sa.Column("vehicle_type", sa.String(length=20), nullable=True),
    )

    op.execute("UPDATE parts SET vehicle_type = 'both' WHERE vehicle_type IS NULL")

    op.alter_column(
        "parts",
        "vehicle_type",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default="both",
    )


def downgrade() -> None:
    op.drop_column("parts", "vehicle_type")