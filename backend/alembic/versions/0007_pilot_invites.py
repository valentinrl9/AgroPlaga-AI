"""Pilot invites table

Revision ID: 0007_pilot_invites
Revises: 0006_scan_farm
Create Date: 2026-06-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_pilot_invites"
down_revision = "0006_scan_farm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pilot_invites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="farmer"),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column("max_uses", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("uses_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("redeemed_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["redeemed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pilot_invites_code", "pilot_invites", ["code"], unique=True)
    op.create_index("ix_pilot_invites_id", "pilot_invites", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_pilot_invites_id", table_name="pilot_invites")
    op.drop_index("ix_pilot_invites_code", table_name="pilot_invites")
    op.drop_table("pilot_invites")
