from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.db.base import Base


class FarmTreatment(Base):
    __tablename__ = "farm_treatments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=True)
    product_name = Column(String(200), nullable=False)
    registry_number = Column(String(40), nullable=True)
    active_substance = Column(String(120), nullable=True)
    applied_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    safety_hours = Column(Integer, nullable=False)
    dose_ml = Column(Float, nullable=True)
    notes = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="active")
