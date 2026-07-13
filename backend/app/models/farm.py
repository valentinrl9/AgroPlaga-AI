from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.db.base import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    crop = Column(String(50), nullable=False)
    farm_type = Column(String(20), nullable=False, default="farm")
    zone_id = Column(Integer, ForeignKey("agri_zones.id"), nullable=True)
    surface_m2 = Column(Float, nullable=True)
    sigpac_code = Column(String(20), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
