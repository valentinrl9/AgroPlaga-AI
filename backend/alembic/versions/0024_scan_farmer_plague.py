"""Allow farmer to override AI plague on their scan."""

from alembic import op
import sqlalchemy as sa

revision = "0024_scan_farmer_plague"
down_revision = "0023_user_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("scans", sa.Column("farmer_plague", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("scans", "farmer_plague")
