"""MAPA catalog sync metadata + extended biocide fields.

Revision ID: 0014_mapa_etl
Revises: 0013_farm_treatments
Create Date: 2026-07-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0014_mapa_etl"
down_revision = "0013_farm_treatments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("biocide_products", sa.Column("mapa_product_id", sa.Integer(), nullable=True))
    op.add_column("biocide_products", sa.Column("agent_name", sa.String(length=200), nullable=True))
    op.add_column("biocide_products", sa.Column("dose_unit", sa.String(length=30), nullable=True))
    op.add_column("biocide_products", sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("biocide_products", sa.Column("source", sa.String(length=30), nullable=False, server_default="mapa_cex"))
    op.add_column("biocide_products", sa.Column("product_status", sa.String(length=30), nullable=False, server_default="vigente"))
    op.create_index("ix_biocide_products_registry_no", "biocide_products", ["registry_no"])
    op.create_unique_constraint(
        "uq_biocide_registry_plague_crop",
        "biocide_products",
        ["registry_no", "plague", "crop"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_biocide_registry_plague_crop", "biocide_products", type_="unique")
    op.drop_index("ix_biocide_products_registry_no", table_name="biocide_products")
    op.drop_column("biocide_products", "product_status")
    op.drop_column("biocide_products", "source")
    op.drop_column("biocide_products", "synced_at")
    op.drop_column("biocide_products", "dose_unit")
    op.drop_column("biocide_products", "agent_name")
    op.drop_column("biocide_products", "mapa_product_id")
