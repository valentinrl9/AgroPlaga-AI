"""Link outbreak events to scans and support perito correction on map.

Revision ID: 0012_outbreak_scan_validation_link
Revises: 0011_climate_tables
Create Date: 2026-07-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0012_outbreak_scan_link"
down_revision = "0011_climate_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("outbreak_events", sa.Column("source_scan_id", sa.Integer(), nullable=True))
    op.add_column("outbreak_events", sa.Column("original_plague", sa.String(length=50), nullable=True))
    op.add_column("outbreak_events", sa.Column("corrected_plague", sa.String(length=50), nullable=True))
    op.add_column(
        "outbreak_events",
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
    )
    op.create_foreign_key(
        "fk_outbreak_events_source_scan_id",
        "outbreak_events",
        "scans",
        ["source_scan_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_outbreak_events_source_scan_id", "outbreak_events", ["source_scan_id"])
    op.create_index("ix_outbreak_events_status", "outbreak_events", ["status"])

    op.execute("UPDATE outbreak_events SET original_plague = plague WHERE original_plague IS NULL")
    op.execute("UPDATE outbreak_events SET status = 'validated' WHERE validated = TRUE")
    op.execute("UPDATE outbreak_events SET status = 'pending' WHERE validated = FALSE")

    op.alter_column("outbreak_events", "status", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_outbreak_events_status", table_name="outbreak_events")
    op.drop_index("ix_outbreak_events_source_scan_id", table_name="outbreak_events")
    op.drop_constraint("fk_outbreak_events_source_scan_id", "outbreak_events", type_="foreignkey")
    op.drop_column("outbreak_events", "status")
    op.drop_column("outbreak_events", "corrected_plague")
    op.drop_column("outbreak_events", "original_plague")
    op.drop_column("outbreak_events", "source_scan_id")
