"""Incidencia fitosanitaria — ciclo CRM V2."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base

INCIDENT_STAGES = (
    "detection",
    "diagnosis",
    "prescription",
    "treatment",
    "evaluation",
    "closed",
)

CLOSURE_OUTCOMES = ("resolved", "crop_lost")


class PestIncident(Base):
    __tablename__ = "pest_incidents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, unique=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True, index=True)
    zone_id = Column(Integer, ForeignKey("agri_zones.id"), nullable=False, index=True)
    outbreak_event_id = Column(Integer, ForeignKey("outbreak_events.id"), nullable=True, index=True)

    plague = Column(String(50), nullable=False, index=True)
    crop = Column(String(50), nullable=False)
    severity = Column(SmallInteger, nullable=False)
    stage = Column(String(20), nullable=False, default="detection", index=True)
    closure_outcome = Column(String(20), nullable=True)

    prescription_product_name = Column(String(200), nullable=True)
    prescription_registry_number = Column(String(40), nullable=True)
    prescription_active_substance = Column(String(120), nullable=True)
    prescription_dose_ml = Column(Float, nullable=True)
    prescription_safety_hours = Column(Integer, nullable=True)
    treatment_id = Column(Integer, ForeignKey("farm_treatments.id"), nullable=True, index=True)
    evaluation_scan_id = Column(Integer, ForeignKey("scans.id"), nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    scan = relationship("Scan", foreign_keys=[scan_id])
    farm = relationship("Farm", foreign_keys=[farm_id])
