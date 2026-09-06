"""Preferencias de notificación push (Fase 5).

Revision ID: 0028_notification_preferences
Revises: 0027_device_tokens
"""

from alembic import op
import sqlalchemy as sa

revision = "0028_notification_preferences"
down_revision = "0027_device_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_notification_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("push_scan_validation", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("push_incidents", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("push_carencia", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("push_alerts_comarcal", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("push_badges", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("push_weekly", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("push_tech_pending", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("quiet_hours_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("quiet_hours_start", sa.Integer(), nullable=False, server_default="22"),
        sa.Column("quiet_hours_end", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_user_notification_preferences_user_id", "user_notification_preferences", ["user_id"])

    op.create_table(
        "notification_push_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=True),
        sa.Column("is_grouped", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_push_log_user_id", "notification_push_log", ["user_id"])
    op.create_index("ix_notification_push_log_sent_at", "notification_push_log", ["sent_at"])


def downgrade() -> None:
    op.drop_index("ix_notification_push_log_sent_at", table_name="notification_push_log")
    op.drop_index("ix_notification_push_log_user_id", table_name="notification_push_log")
    op.drop_table("notification_push_log")
    op.drop_index("ix_user_notification_preferences_user_id", table_name="user_notification_preferences")
    op.drop_table("user_notification_preferences")
