"""Estaciones meteorológicas NEXO Climate — sur de Almería."""

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String

from app.db.base import Base


class ClimateStation(Base):
    __tablename__ = "climate_stations"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    zone_id = Column(Integer, ForeignKey("agri_zones.id"), nullable=True, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    source = Column(String(30), nullable=False, default="openmeteo")
    active = Column(Boolean, nullable=False, default=True)
