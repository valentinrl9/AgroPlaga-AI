"""Farm treatments + biocide catalog stub for Field Premium.

Revision ID: 0013_farm_treatments
Revises: 0012_outbreak_scan_link
Create Date: 2026-07-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0013_farm_treatments"
down_revision = "0012_outbreak_scan_link"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("farms", sa.Column("surface_m2", sa.Float(), nullable=True))

    op.create_table(
        "biocide_products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("registry_no", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("active_substance", sa.String(length=120), nullable=True),
        sa.Column("plague", sa.String(length=50), nullable=False),
        sa.Column("crop", sa.String(length=50), nullable=False),
        sa.Column("dose_min_l_ha", sa.Float(), nullable=False),
        sa.Column("dose_max_l_ha", sa.Float(), nullable=False),
        sa.Column("safety_hours", sa.Integer(), nullable=False, server_default="48"),
    )
    op.create_index("ix_biocide_products_plague_crop", "biocide_products", ["plague", "crop"])

    op.create_table(
        "farm_treatments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=True, index=True),
        sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=True),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("registry_number", sa.String(length=40), nullable=True),
        sa.Column("active_substance", sa.String(length=120), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("safety_hours", sa.Integer(), nullable=False),
        sa.Column("dose_ml", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
    )

    op.execute(
        """
        INSERT INTO biocide_products (registry_no, name, active_substance, plague, crop, dose_min_l_ha, dose_max_l_ha, safety_hours)
        VALUES
        ('ES-00001', 'Spintor 480 SC', 'spinosad', 'tuta absoluta', 'tomate', 0.06, 0.09, 72),
        ('ES-00002', 'Confidor 200 SL', 'imidacloprid', 'mosca blanca', 'tomate', 0.3, 0.5, 48),
        ('ES-00003', 'Vertimec 1.8 EC', 'abamectina', 'arañuela roja', 'tomate', 0.2, 0.3, 48),
        ('ES-00004', 'Previcur Energy', 'propamocarb', 'mildiu', 'tomate', 1.5, 2.0, 120),
        ('ES-00005', 'Amistar', 'azoxistrobin', 'oídio', 'tomate', 0.6, 0.8, 96)
        """
    )


def downgrade() -> None:
    op.drop_table("farm_treatments")
    op.drop_index("ix_biocide_products_plague_crop", table_name="biocide_products")
    op.drop_table("biocide_products")
    op.drop_column("farms", "surface_m2")
