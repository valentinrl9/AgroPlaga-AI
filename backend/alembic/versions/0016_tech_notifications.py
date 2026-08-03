"""Notificaciones perito — escaneos pendientes de validación.

Revision ID: 0016_tech_notifications
Revises: 0015_siex_cuaderno
"""

from alembic import op
import sqlalchemy as sa

revision = "0016_tech_notifications"
down_revision = "0015_siex_cuaderno"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tech_notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False),
        sa.Column("notification_type", sa.String(length=40), nullable=False, server_default="scan_pending"),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tech_notifications_recipient_id", "tech_notifications", ["recipient_id"])
    op.create_index("ix_tech_notifications_scan_id", "tech_notifications", ["scan_id"])
    op.create_index("ix_tech_notifications_is_read", "tech_notifications", ["is_read"])


def downgrade() -> None:
    op.drop_index("ix_tech_notifications_is_read", table_name="tech_notifications")
    op.drop_index("ix_tech_notifications_scan_id", table_name="tech_notifications")
    op.drop_index("ix_tech_notifications_recipient_id", table_name="tech_notifications")
    op.drop_table("tech_notifications")
