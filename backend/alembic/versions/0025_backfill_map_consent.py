"""Backfill consent_accepted_at for farmers registered before the consent column."""

from alembic import op

revision = "0025_backfill_map_consent"
down_revision = "0024_scan_farmer_plague"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE users
        SET consent_accepted_at = NOW()
        WHERE consent_accepted_at IS NULL
          AND role = 'farmer'
        """
    )


def downgrade() -> None:
    pass
