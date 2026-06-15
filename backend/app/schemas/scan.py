from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScanCreate(BaseModel):
    crop: str
    plague: str
    confidence: float
    severity: str
    location: str | None = None
    farm_id: int | None = None


class ScanRead(BaseModel):
    id: int
    crop: str
    plague: str
    confidence: float
    severity: str
    location: str | None = None
    farm_id: int | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
