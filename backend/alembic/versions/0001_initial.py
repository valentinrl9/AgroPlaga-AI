"""Initial database schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-27 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="farmer"),
    )

    op.create_table(
        "scans",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("crop", sa.String(), nullable=False),
        sa.Column("plague", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
    )

    op.create_table(
        "outbreaks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("plague", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("reported_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("outbreaks")
    op.drop_table("scans")
    op.drop_table("users")
