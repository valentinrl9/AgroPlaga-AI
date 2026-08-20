"""Prescription treated surface on pest incidents.

Revision ID: 0021_incident_prescription_surface
Revises: 0020_climate_multi_station
Create Date: 2026-07-11
"""

from alembic import op
import sqlalchemy as sa

revision = "0021_prescription_surface"
down_revision = "0020_climate_multi_station"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pest_incidents", sa.Column("prescription_surface_m2", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("pest_incidents", "prescription_surface_m2")
