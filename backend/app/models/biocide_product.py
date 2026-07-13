from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.base import Base


class BiocideProduct(Base):
    __tablename__ = "biocide_products"

    id = Column(Integer, primary_key=True, index=True)
    mapa_product_id = Column(Integer, nullable=True)
    registry_no = Column(String(40), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    active_substance = Column(String(120), nullable=True)
    plague = Column(String(50), nullable=False)
    crop = Column(String(50), nullable=False)
    dose_min_l_ha = Column(Float, nullable=False)
    dose_max_l_ha = Column(Float, nullable=False)
    dose_unit = Column(String(30), nullable=True)
    agent_name = Column(String(200), nullable=True)
    safety_hours = Column(Integer, nullable=False, default=48)
    synced_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(30), nullable=False, default="mapa_cex")
    product_status = Column(String(30), nullable=False, default="vigente")
