"""Phase 6: gamification, feedback ML, farms

Revision ID: 0004_phase6
Revises: 0003_alert_preferences
Create Date: 2026-06-11
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_phase6"
down_revision = "0003_alert_preferences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("feedback", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("feedback", sa.Column("is_correct", sa.Boolean(), nullable=True))
    op.add_column("feedback", sa.Column("corrected_plague", sa.String(length=50), nullable=True))

    op.create_table(
        "user_badges",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("badge_code", sa.String(length=50), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "badge_code", name="uq_user_badge"),
    )
    op.create_index("ix_user_badges_user_id", "user_badges", ["user_id"])

    op.create_table(
        "farms",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("crop", sa.String(length=50), nullable=False),
        sa.Column("farm_type", sa.String(length=20), nullable=False, server_default="farm"),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("agri_zones.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_farms_user_id", "farms", ["user_id"])

    op.create_table(
        "contribution_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("agri_zones.id"), nullable=False),
        sa.Column("plague", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_contribution_logs_user_id", "contribution_logs", ["user_id"])
    op.create_index("ix_contribution_logs_created_at", "contribution_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_contribution_logs_created_at", table_name="contribution_logs")
    op.drop_index("ix_contribution_logs_user_id", table_name="contribution_logs")
    op.drop_table("contribution_logs")
    op.drop_index("ix_farms_user_id", table_name="farms")
    op.drop_table("farms")
    op.drop_index("ix_user_badges_user_id", table_name="user_badges")
    op.drop_table("user_badges")
    op.drop_column("feedback", "corrected_plague")
    op.drop_column("feedback", "is_correct")
    op.drop_column("feedback", "user_id")
