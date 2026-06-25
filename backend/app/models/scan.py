from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop = Column(String, nullable=False)
    plague = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    severity = Column(String, nullable=False)
    location = Column(String, nullable=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    image_path = Column(String(255), nullable=True)
    share_with_tech = Column(Boolean, default=False, nullable=False, index=True)
    tech_status = Column(String(20), nullable=True, index=True)
    corrected_plague = Column(String(50), nullable=True)
    tech_notes = Column(String(500), nullable=True)
    validated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    user = relationship("User", foreign_keys=[user_id])
    validated_by = relationship("User", foreign_keys=[validated_by_id])
