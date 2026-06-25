from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScanCreate(BaseModel):
    crop: str
    plague: str
    confidence: float
    severity: str
    location: str | None = None
    farm_id: int | None = None
    share_with_tech: bool = False


class ScanRead(BaseModel):
    id: int
    crop: str
    plague: str
    confidence: float
    severity: str
    location: str | None = None
    farm_id: int | None = None
    created_at: datetime | None = None
    share_with_tech: bool = False
    tech_status: str | None = None
    corrected_plague: str | None = None
    tech_notes: str | None = None
    validated_at: datetime | None = None
    has_image: bool = False

    model_config = ConfigDict(from_attributes=True)


class ScanValidateRequest(BaseModel):
    action: Literal["confirm", "correct", "reject"]
    corrected_plague: str | None = Field(default=None, max_length=50)
    tech_notes: str | None = Field(default=None, max_length=500)

    @field_validator("corrected_plague")
    @classmethod
    def normalize_plague(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower() or None


class TechScanQueueItem(BaseModel):
    id: int
    crop: str
    plague: str
    confidence: float
    severity: str
    farm_id: int | None
    farm_name: str | None
    farmer_id: int
    farmer_name: str
    farmer_email: str
    created_at: datetime
    share_with_tech: bool
    tech_status: str | None
    has_image: bool = True


class PilotFarmerItem(BaseModel):
    id: int
    name: str
    email: str
    shared_scans: int
    pending_scans: int
    status: Literal["inactive", "ok", "pending"]
