"""Add created_at to scans for weekly vigilance

Revision ID: 0005_scan_timestamps
Revises: 0004_phase6
Create Date: 2026-06-11
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_scan_timestamps"
down_revision = "0004_phase6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scans",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_scans_created_at", "scans", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_scans_created_at", table_name="scans")
    op.drop_column("scans", "created_at")
