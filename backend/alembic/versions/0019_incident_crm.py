"""CRM incidencias — prescripción, tratamiento y evaluación.

Revision ID: 0019_incident_crm
Revises: 0018_pest_incidents
"""

from alembic import op
import sqlalchemy as sa

revision = "0019_incident_crm"
down_revision = "0018_pest_incidents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pest_incidents", sa.Column("prescription_product_name", sa.String(length=200), nullable=True))
    op.add_column("pest_incidents", sa.Column("prescription_registry_number", sa.String(length=40), nullable=True))
    op.add_column("pest_incidents", sa.Column("prescription_active_substance", sa.String(length=120), nullable=True))
    op.add_column("pest_incidents", sa.Column("prescription_dose_ml", sa.Float(), nullable=True))
    op.add_column("pest_incidents", sa.Column("prescription_safety_hours", sa.Integer(), nullable=True))
    op.add_column("pest_incidents", sa.Column("treatment_id", sa.Integer(), sa.ForeignKey("farm_treatments.id"), nullable=True))
    op.add_column("pest_incidents", sa.Column("evaluation_scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=True))
    op.create_index("ix_pest_incidents_treatment_id", "pest_incidents", ["treatment_id"])


def downgrade() -> None:
    op.drop_index("ix_pest_incidents_treatment_id", table_name="pest_incidents")
    op.drop_column("pest_incidents", "evaluation_scan_id")
    op.drop_column("pest_incidents", "treatment_id")
    op.drop_column("pest_incidents", "prescription_safety_hours")
    op.drop_column("pest_incidents", "prescription_dose_ml")
    op.drop_column("pest_incidents", "prescription_active_substance")
    op.drop_column("pest_incidents", "prescription_registry_number")
    op.drop_column("pest_incidents", "prescription_product_name")
