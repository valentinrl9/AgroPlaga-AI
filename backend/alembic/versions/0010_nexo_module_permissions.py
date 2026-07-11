"""NEXO Agro module permission flags on users.

Revision ID: 0010_nexo_module_permissions
Revises: 0009_contact_inquiries
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_nexo_module_permissions"
down_revision = "0009_contact_inquiries"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("has_field_premium", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("has_climate_module", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("has_siex_enterprise", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "has_field_premium", server_default=None)
    op.alter_column("users", "has_climate_module", server_default=None)
    op.alter_column("users", "has_siex_enterprise", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "has_siex_enterprise")
    op.drop_column("users", "has_climate_module")
    op.drop_column("users", "has_field_premium")
