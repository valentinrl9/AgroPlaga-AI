"""User is_active and token_version for auth hardening."""

from alembic import op
import sqlalchemy as sa

revision = "0023_user_security"
down_revision = "0022_farm_climate_station"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("users", "token_version")
    op.drop_column("users", "is_active")
