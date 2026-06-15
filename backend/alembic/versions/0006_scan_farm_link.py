"""Link scans to farms for personal analytics

Revision ID: 0006_scan_farm
Revises: 0005_scan_timestamps
Create Date: 2026-06-11
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_scan_farm"
down_revision = "0005_scan_timestamps"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("scans", sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=True))
    op.create_index("ix_scans_farm_id", "scans", ["farm_id"])


def downgrade() -> None:
    op.drop_index("ix_scans_farm_id", table_name="scans")
    op.drop_column("scans", "farm_id")
