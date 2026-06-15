from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("agri_zones.id"), nullable=False, index=True)
    plague = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    priority_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False)
