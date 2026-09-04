"""Notificaciones in-app agricultor + log recordatorios.

Revision ID: 0026_user_notifications
Revises: 0025_backfill_map_consent
"""

from alembic import op
import sqlalchemy as sa

revision = "0026_user_notifications"
down_revision = "0025_backfill_map_consent"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column("section", sa.String(length=30), nullable=False, server_default="home"),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("reference_type", sa.String(length=30), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("dedupe_key", sa.String(length=120), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_notifications_user_id", "user_notifications", ["user_id"])
    op.create_index("ix_user_notifications_is_read", "user_notifications", ["is_read"])
    op.create_index("ix_user_notifications_dedupe_key", "user_notifications", ["dedupe_key"])
    op.create_index("ix_user_notifications_created_at", "user_notifications", ["created_at"])

    op.create_table(
        "notification_reminder_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("dedupe_key", sa.String(length=120), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "dedupe_key", name="uq_reminder_log_user_dedupe"),
    )
    op.create_index("ix_notification_reminder_log_user_id", "notification_reminder_log", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_notification_reminder_log_user_id", table_name="notification_reminder_log")
    op.drop_table("notification_reminder_log")
    op.drop_index("ix_user_notifications_created_at", table_name="user_notifications")
    op.drop_index("ix_user_notifications_dedupe_key", table_name="user_notifications")
    op.drop_index("ix_user_notifications_is_read", table_name="user_notifications")
    op.drop_index("ix_user_notifications_user_id", table_name="user_notifications")
    op.drop_table("user_notifications")
