"""Contact form inquiries from public landing page.

Revision ID: 0009_contact_inquiries
Revises: 0008_scan_tech_validation
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_contact_inquiries"
down_revision = "0008_scan_tech_validation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contact_inquiries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contact_inquiries_id", "contact_inquiries", ["id"], unique=False)
    op.create_index("ix_contact_inquiries_created_at", "contact_inquiries", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_contact_inquiries_created_at", table_name="contact_inquiries")
    op.drop_index("ix_contact_inquiries_id", table_name="contact_inquiries")
    op.drop_table("contact_inquiries")
