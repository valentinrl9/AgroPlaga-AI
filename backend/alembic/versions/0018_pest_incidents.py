"""Incidencias fitosanitarias V2.

Revision ID: 0018_pest_incidents
Revises: 0017_v2_data_foundations
"""

from alembic import op
import sqlalchemy as sa

revision = "0018_pest_incidents"
down_revision = "0017_v2_data_foundations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pest_incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False),
        sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=True),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("agri_zones.id"), nullable=False),
        sa.Column("outbreak_event_id", sa.Integer(), sa.ForeignKey("outbreak_events.id"), nullable=True),
        sa.Column("plague", sa.String(length=50), nullable=False),
        sa.Column("crop", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.SmallInteger(), nullable=False),
        sa.Column("stage", sa.String(length=20), nullable=False, server_default="detection"),
        sa.Column("closure_outcome", sa.String(length=20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("scan_id", name="uq_pest_incidents_scan_id"),
    )
    op.create_index("ix_pest_incidents_user_id", "pest_incidents", ["user_id"])
    op.create_index("ix_pest_incidents_stage", "pest_incidents", ["stage"])
    op.create_index("ix_pest_incidents_plague", "pest_incidents", ["plague"])


def downgrade() -> None:
    op.drop_index("ix_pest_incidents_plague", table_name="pest_incidents")
    op.drop_index("ix_pest_incidents_stage", table_name="pest_incidents")
    op.drop_index("ix_pest_incidents_user_id", table_name="pest_incidents")
    op.drop_table("pest_incidents")
