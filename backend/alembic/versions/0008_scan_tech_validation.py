"""Scan tech validation and images (v1.6-core)

Revision ID: 0008_scan_tech_validation
Revises: 0007_pilot_invites
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_scan_tech_validation"
down_revision = "0007_pilot_invites"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("scans", sa.Column("image_path", sa.String(length=255), nullable=True))
    op.add_column(
        "scans",
        sa.Column("share_with_tech", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("scans", sa.Column("tech_status", sa.String(length=20), nullable=True))
    op.add_column("scans", sa.Column("corrected_plague", sa.String(length=50), nullable=True))
    op.add_column("scans", sa.Column("tech_notes", sa.String(length=500), nullable=True))
    op.add_column("scans", sa.Column("validated_by_id", sa.Integer(), nullable=True))
    op.add_column("scans", sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "fk_scans_validated_by_id_users",
        "scans",
        "users",
        ["validated_by_id"],
        ["id"],
    )
    op.create_index("ix_scans_tech_status", "scans", ["tech_status"], unique=False)
    op.create_index("ix_scans_share_with_tech", "scans", ["share_with_tech"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scans_share_with_tech", table_name="scans")
    op.drop_index("ix_scans_tech_status", table_name="scans")
    op.drop_constraint("fk_scans_validated_by_id_users", "scans", type_="foreignkey")
    op.drop_column("scans", "validated_at")
    op.drop_column("scans", "validated_by_id")
    op.drop_column("scans", "tech_notes")
    op.drop_column("scans", "corrected_plague")
    op.drop_column("scans", "tech_status")
    op.drop_column("scans", "share_with_tech")
    op.drop_column("scans", "image_path")
