"""Climate multi-estación sur de Almería.

Revision ID: 0020_climate_multi_station
Revises: 0019_incident_crm
"""

from alembic import op
import sqlalchemy as sa

revision = "0020_climate_multi_station"
down_revision = "0019_incident_crm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "climate_stations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("agri_zones.id"), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="openmeteo"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_climate_stations_zone_id", "climate_stations", ["zone_id"])

    op.execute(
        """
        INSERT INTO climate_stations (id, slug, name, lat, lon, source, active)
        VALUES (1, 'poniente', 'Poniente (La Mojonera)', 36.77, -2.81, 'openmeteo', true)
        """
    )

    op.add_column(
        "climate_daily",
        sa.Column("station_id", sa.Integer(), nullable=False, server_default="1"),
    )
    op.drop_constraint("climate_daily_pkey", "climate_daily", type_="primary")
    op.create_primary_key("climate_daily_pkey", "climate_daily", ["station_id", "fecha"])
    op.create_foreign_key(
        "fk_climate_daily_station_id",
        "climate_daily",
        "climate_stations",
        ["station_id"],
        ["id"],
    )
    op.alter_column("climate_daily", "station_id", server_default=None)

    op.add_column(
        "climate_weekly",
        sa.Column("station_id", sa.Integer(), nullable=False, server_default="1"),
    )
    op.drop_constraint("climate_weekly_pkey", "climate_weekly", type_="primary")
    op.create_primary_key("climate_weekly_pkey", "climate_weekly", ["station_id", "semana_id"])
    op.create_foreign_key(
        "fk_climate_weekly_station_id",
        "climate_weekly",
        "climate_stations",
        ["station_id"],
        ["id"],
    )
    op.alter_column("climate_weekly", "station_id", server_default=None)

    op.add_column(
        "climate_monthly",
        sa.Column("station_id", sa.Integer(), nullable=False, server_default="1"),
    )
    op.drop_constraint("climate_monthly_pkey", "climate_monthly", type_="primary")
    op.create_primary_key("climate_monthly_pkey", "climate_monthly", ["station_id", "mes"])
    op.create_foreign_key(
        "fk_climate_monthly_station_id",
        "climate_monthly",
        "climate_stations",
        ["station_id"],
        ["id"],
    )
    op.alter_column("climate_monthly", "station_id", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_climate_monthly_station_id", "climate_monthly", type_="foreignkey")
    op.drop_constraint("climate_monthly_pkey", "climate_monthly", type_="primary")
    op.drop_column("climate_monthly", "station_id")
    op.create_primary_key("climate_monthly_pkey", "climate_monthly", ["mes"])

    op.drop_constraint("fk_climate_weekly_station_id", "climate_weekly", type_="foreignkey")
    op.drop_constraint("climate_weekly_pkey", "climate_weekly", type_="primary")
    op.drop_column("climate_weekly", "station_id")
    op.create_primary_key("climate_weekly_pkey", "climate_weekly", ["semana_id"])

    op.drop_constraint("fk_climate_daily_station_id", "climate_daily", type_="foreignkey")
    op.drop_constraint("climate_daily_pkey", "climate_daily", type_="primary")
    op.drop_column("climate_daily", "station_id")
    op.create_primary_key("climate_daily_pkey", "climate_daily", ["fecha"])

    op.drop_index("ix_climate_stations_zone_id", table_name="climate_stations")
    op.drop_table("climate_stations")
