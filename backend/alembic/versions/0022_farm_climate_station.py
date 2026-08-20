"""Estación meteorológica preferida por finca (override manual).

Revision ID: 0022_farm_climate_station
Revises: 0021_prescription_surface
"""

from alembic import op
import sqlalchemy as sa

revision = "0022_farm_climate_station"
down_revision = "0021_prescription_surface"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("farms", sa.Column("climate_station_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_farms_climate_station_id",
        "farms",
        "climate_stations",
        ["climate_station_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_farms_climate_station_id", "farms", type_="foreignkey")
    op.drop_column("farms", "climate_station_id")
