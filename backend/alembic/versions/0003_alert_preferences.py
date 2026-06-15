"""User alert preferences

Revision ID: 0003_alert_preferences
Revises: 0002_community
Create Date: 2026-06-11
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_alert_preferences"
down_revision = "0002_community"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_alert_preferences",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plague", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("user_id", "plague", name="uq_user_plague_pref"),
    )
    op.create_index("ix_user_alert_preferences_user_id", "user_alert_preferences", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_alert_preferences_user_id", table_name="user_alert_preferences")
    op.drop_table("user_alert_preferences")
