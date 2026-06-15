from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry

from app.db.base import Base


class AgriZone(Base):
    """Zona agraria de referencia SIGPAC a nivel municipio (sin parcela)."""

    __tablename__ = "agri_zones"

    id = Column(Integer, primary_key=True, index=True)
    sigpac_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    province = Column(String(50), nullable=False, default="Almería")
    municipality_code = Column(String(10), nullable=False)
    centroid = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
