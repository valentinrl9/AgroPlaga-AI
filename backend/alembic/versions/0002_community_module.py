"""Community module: PostGIS, SIGPAC zones, outbreak_events, alerts

Revision ID: 0002_community
Revises: 0001_initial
Create Date: 2026-06-10
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0002_community"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.add_column(
        "users",
        sa.Column("contribution_count", sa.Integer(), nullable=False, server_default="0"),
    )

    op.drop_table("outbreaks")

    op.create_table(
        "agri_zones",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("sigpac_code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("province", sa.String(length=50), nullable=False, server_default="Almería"),
        sa.Column("municipality_code", sa.String(length=10), nullable=False),
        sa.Column("centroid", Geometry(geometry_type="POINT", srid=4326), nullable=False),
    )
    op.create_index("ix_agri_zones_sigpac_code", "agri_zones", ["sigpac_code"], unique=True)

    op.create_table(
        "outbreak_events",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("plague", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.SmallInteger(), nullable=False),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("agri_zones.id"), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("model_version", sa.String(length=10), nullable=False, server_default="v0.0"),
        sa.Column("validated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("validated_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_outbreak_events_plague", "outbreak_events", ["plague"])
    op.create_index("ix_outbreak_events_zone_id", "outbreak_events", ["zone_id"])
    op.create_index("ix_outbreak_events_reported_at", "outbreak_events", ["reported_at"])
    op.execute(
        "CREATE INDEX ix_outbreak_events_geom ON outbreak_events USING GIST (geom)"
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("agri_zones.id"), nullable=False),
        sa.Column("plague", sa.String(length=50), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_alerts_zone_id", "alerts", ["zone_id"])
    op.create_index("ix_alerts_plague", "alerts", ["plague"])
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_index("ix_outbreak_events_geom", table_name="outbreak_events")
    op.drop_table("outbreak_events")
    op.drop_index("ix_agri_zones_sigpac_code", table_name="agri_zones")
    op.drop_table("agri_zones")

    op.create_table(
        "outbreaks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("plague", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("reported_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.drop_column("users", "contribution_count")
