"""NEXO Climate — tablas agregadas Open-Meteo.

Revision ID: 0011_climate_tables
Revises: 0010_nexo_module_permissions
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_climate_tables"
down_revision = "0010_nexo_module_permissions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "climate_daily",
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("et0_diaria", sa.Float(), nullable=True),
        sa.Column("radiacion_diaria", sa.Float(), nullable=True),
        sa.Column("temperatura_media", sa.Float(), nullable=True),
        sa.Column("humedad_media", sa.Float(), nullable=True),
        sa.Column("viento_medio", sa.Float(), nullable=True),
        sa.Column("precipitacion_diaria", sa.Float(), nullable=True),
        sa.Column("estres_termico_medio", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("fecha"),
    )
    op.create_table(
        "climate_weekly",
        sa.Column("semana_id", sa.String(length=10), nullable=False),
        sa.Column("et0_semanal", sa.Float(), nullable=True),
        sa.Column("radiacion_semanal", sa.Float(), nullable=True),
        sa.Column("temperatura_media_semanal", sa.Float(), nullable=True),
        sa.Column("humedad_media_semanal", sa.Float(), nullable=True),
        sa.Column("viento_medio_semanal", sa.Float(), nullable=True),
        sa.Column("precipitacion_semanal", sa.Float(), nullable=True),
        sa.Column("estres_termico_semanal", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("semana_id"),
    )
    op.create_table(
        "climate_monthly",
        sa.Column("mes", sa.String(length=7), nullable=False),
        sa.Column("et0_mensual", sa.Float(), nullable=True),
        sa.Column("radiacion_mensual", sa.Float(), nullable=True),
        sa.Column("temperatura_media_mes", sa.Float(), nullable=True),
        sa.Column("humedad_media_mes", sa.Float(), nullable=True),
        sa.Column("viento_medio_mes", sa.Float(), nullable=True),
        sa.Column("precipitacion_mensual", sa.Float(), nullable=True),
        sa.Column("estres_termico_mes", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("mes"),
    )


def downgrade() -> None:
    op.drop_table("climate_monthly")
    op.drop_table("climate_weekly")
    op.drop_table("climate_daily")
