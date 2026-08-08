"""V2 cimientos de datos — municipios, fincas, consentimiento, GPS escaneos.

Revision ID: 0017_v2_data_foundations
Revises: 0016_tech_notifications
"""

from alembic import op
import sqlalchemy as sa

revision = "0017_v2_data_foundations"
down_revision = "0016_tech_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("consent_accepted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("farms", sa.Column("nave", sa.String(length=100), nullable=True))
    op.add_column("farms", sa.Column("sector", sa.String(length=100), nullable=True))
    op.add_column("farms", sa.Column("crop_stage", sa.String(length=50), nullable=True))
    op.add_column("farms", sa.Column("crop_variant", sa.String(length=50), nullable=True))
    op.add_column("scans", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("scans", sa.Column("longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("scans", "longitude")
    op.drop_column("scans", "latitude")
    op.drop_column("farms", "crop_variant")
    op.drop_column("farms", "crop_stage")
    op.drop_column("farms", "sector")
    op.drop_column("farms", "nave")
    op.drop_column("users", "consent_accepted_at")
