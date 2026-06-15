from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
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
    user = relationship("User")
