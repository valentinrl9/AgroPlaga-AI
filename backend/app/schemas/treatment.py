from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BiocideProductRead(BaseModel):
    id: int
    registry_no: str
    name: str
    active_substance: str | None
    plague: str
    crop: str
    dose_min_l_ha: float
    dose_max_l_ha: float
    dose_unit: str | None = None
    agent_name: str | None = None
    safety_hours: int
    source: str = "mapa_cex"

    model_config = ConfigDict(from_attributes=True)


class CatalogStatusRead(BaseModel):
    success: bool | None = None
    synced_at: datetime | None = None
    catalog_date: str | None = None
    products_indexed: int = 0
    stale: bool = False
    disclaimer: str


class DoseCalculateRequest(BaseModel):
    surface_m2: float = Field(gt=0)
    registry_no: str
    plague: str | None = None
    crop: str | None = None
    caldo_l_ha: float = Field(default=1000.0, gt=0)


class DoseCalculateResponse(BaseModel):
    registry_no: str
    product_name: str
    dose_l_ha: float
    dose_ml: float
    safety_hours: int


class TreatmentCreate(BaseModel):
    farm_id: int | None = None
    scan_id: int | None = None
    product_name: str = Field(max_length=200)
    registry_number: str | None = Field(default=None, max_length=40)
    active_substance: str | None = Field(default=None, max_length=120)
    safety_hours: int = Field(ge=1, le=720)
    dose_ml: float | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=500)
    ack_unverified: bool = False


class TreatmentRead(BaseModel):
    id: int
    farm_id: int | None
    scan_id: int | None
    product_name: str
    registry_number: str | None
    active_substance: str | None
    applied_at: datetime
    safety_hours: int
    dose_ml: float | None
    notes: str | None
    status: str
    hours_remaining: float | None = None
    harvest_allowed: bool = False
    siex_entry_id: int | None = None
    siex_message: str | None = None
    scan_verification: str | None = None

    model_config = ConfigDict(from_attributes=True)
