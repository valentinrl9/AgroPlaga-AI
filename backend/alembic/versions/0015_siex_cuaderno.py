"""SIEX cuaderno borrador + sigpac en fincas + has_siex_module.

Revision ID: 0015_siex_cuaderno
Revises: 0014_mapa_etl
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa

revision = "0015_siex_cuaderno"
down_revision = "0014_mapa_etl"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("has_siex_module", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("users", "has_siex_module", server_default=None)

    op.add_column("farms", sa.Column("sigpac_code", sa.String(length=20), nullable=True))
    op.create_index("ix_farms_sigpac_code", "farms", ["sigpac_code"])

    op.create_table(
        "siex_cuaderno_borrador",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=True, index=True),
        sa.Column("treatment_id", sa.Integer(), sa.ForeignKey("farm_treatments.id"), nullable=False, index=True),
        sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=True),
        sa.Column("tipo_actuacion", sa.String(length=30), nullable=False, server_default="fitosanitario"),
        sa.Column("sigpac_code", sa.String(length=20), nullable=False),
        sa.Column("farm_name", sa.String(length=100), nullable=True),
        sa.Column("zone_name", sa.String(length=100), nullable=True),
        sa.Column("crop", sa.String(length=50), nullable=False),
        sa.Column("plague", sa.String(length=50), nullable=False),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("registry_number", sa.String(length=40), nullable=True),
        sa.Column("active_substance", sa.String(length=120), nullable=True),
        sa.Column("dose_ml", sa.Float(), nullable=True),
        sa.Column("surface_m2", sa.Float(), nullable=True),
        sa.Column("safety_hours", sa.Integer(), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("que_se_hizo", sa.Text(), nullable=False),
        sa.Column("justificacion", sa.Text(), nullable=False),
        sa.Column("climate_context", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="registrado"),
        sa.Column("tech_notes", sa.String(length=500), nullable=True),
        sa.Column("validated_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_siex_cuaderno_status", "siex_cuaderno_borrador", ["status"])


def downgrade() -> None:
    op.drop_index("ix_siex_cuaderno_status", table_name="siex_cuaderno_borrador")
    op.drop_table("siex_cuaderno_borrador")
    op.drop_index("ix_farms_sigpac_code", table_name="farms")
    op.drop_column("farms", "sigpac_code")
    op.drop_column("users", "has_siex_module")
