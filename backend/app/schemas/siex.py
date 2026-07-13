from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SiexStatus = Literal["registrado", "pendiente_validacion", "validado", "rechazado"]


class SiexEntryRead(BaseModel):
    id: int
    treatment_id: int
    scan_id: int | None
    tipo_actuacion: str
    sigpac_code: str
    farm_name: str | None
    zone_name: str | None
    crop: str
    plague: str
    product_name: str
    registry_number: str | None
    active_substance: str | None
    dose_ml: float | None
    surface_m2: float | None
    safety_hours: int
    applied_at: datetime
    que_se_hizo: str
    justificacion: str
    climate_context: str | None
    status: str
    tech_notes: str | None
    farmer_name: str | None = None
    farmer_email: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SiexEntryValidate(BaseModel):
    action: Literal["approve", "reject"]
    tech_notes: str | None = Field(default=None, max_length=500)


class SiexAccessRead(BaseModel):
    has_access: bool
    has_module: bool
    has_enterprise: bool
    preview_open: bool


class SiexExportPreview(BaseModel):
    exported_at: datetime
    count: int
    entries: list[dict]
