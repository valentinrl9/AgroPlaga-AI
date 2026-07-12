from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, SmallInteger, String
from geoalchemy2 import Geometry

from app.db.base import Base


class OutbreakEvent(Base):
    """Evento colaborativo anonimizado para mapa de calor y alertas."""

    __tablename__ = "outbreak_events"

    id = Column(Integer, primary_key=True, index=True)
    plague = Column(String(50), nullable=False, index=True)
    severity = Column(SmallInteger, nullable=False)
    zone_id = Column(Integer, ForeignKey("agri_zones.id"), nullable=False, index=True)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    reported_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    model_version = Column(String(10), nullable=False, default="v0.0")
    validated = Column(Boolean, default=False, nullable=False)
    validated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    source_scan_id = Column(Integer, ForeignKey("scans.id", ondelete="SET NULL"), nullable=True, index=True)
    original_plague = Column(String(50), nullable=True)
    corrected_plague = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
