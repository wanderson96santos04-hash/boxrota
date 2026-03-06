"""add workshop slug

Revision ID: add_workshop_slug
Revises: 0001_initial
Create Date: 2026-03-06
"""

from alembic import op
import sqlalchemy as sa


# ajuste se sua revisão anterior tiver outro id
revision = "add_workshop_slug"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("workshops", sa.Column("slug", sa.String(length=120), nullable=True))
    op.create_index("ix_workshops_slug", "workshops", ["slug"], unique=False)
    op.create_unique_constraint("uq_workshops_slug", "workshops", ["slug"])

    # preencher registros antigos
    op.execute("""
        UPDATE workshops
        SET slug = LOWER(
            REGEXP_REPLACE(
                REGEXP_REPLACE(COALESCE(name, 'oficina'), '[^a-zA-Z0-9]+', '-', 'g'),
                '(^-+|-+$)', '', 'g'
            )
        )
        WHERE slug IS NULL
    """)

    # se algum slug ficou vazio
    op.execute("""
        UPDATE workshops
        SET slug = 'oficina-' || SUBSTRING(CAST(id AS TEXT), 1, 8)
        WHERE slug IS NULL OR slug = ''
    """)

    op.alter_column("workshops", "slug", nullable=False)


def downgrade():
    op.drop_constraint("uq_workshops_slug", "workshops", type_="unique")
    op.drop_index("ix_workshops_slug", table_name="workshops")
    op.drop_column("workshops", "slug")