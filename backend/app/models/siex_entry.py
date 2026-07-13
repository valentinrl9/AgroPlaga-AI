from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db.base import Base


class SiexCuadernoEntry(Base):
    __tablename__ = "siex_cuaderno_borrador"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True, index=True)
    treatment_id = Column(Integer, ForeignKey("farm_treatments.id"), nullable=False, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=True)
    tipo_actuacion = Column(String(30), nullable=False, default="fitosanitario")
    sigpac_code = Column(String(20), nullable=False)
    farm_name = Column(String(100), nullable=True)
    zone_name = Column(String(100), nullable=True)
    crop = Column(String(50), nullable=False)
    plague = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    registry_number = Column(String(40), nullable=True)
    active_substance = Column(String(120), nullable=True)
    dose_ml = Column(Float, nullable=True)
    surface_m2 = Column(Float, nullable=True)
    safety_hours = Column(Integer, nullable=False)
    applied_at = Column(DateTime(timezone=True), nullable=False)
    que_se_hizo = Column(Text, nullable=False)
    justificacion = Column(Text, nullable=False)
    climate_context = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="registrado", index=True)
    tech_notes = Column(String(500), nullable=True)
    validated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
