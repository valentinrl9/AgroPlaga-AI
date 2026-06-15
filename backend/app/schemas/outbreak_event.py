from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SeverityLevel = Literal[1, 2, 3]


class OutbreakEventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plague: str = Field(..., min_length=2, max_length=50)
    severity: SeverityLevel
    zone_id: int
    model_version: str = Field(default="v0.0", max_length=10)

    @field_validator("plague")
    @classmethod
    def normalize_plague(cls, value: str) -> str:
        return value.strip().lower()


class OutbreakEventRead(BaseModel):
    id: int
    plague: str
    severity: int
    zone_id: int
    zone_name: str | None = None
    reported_at: datetime
    model_version: str
    validated: bool

    model_config = ConfigDict(from_attributes=True)


class OutbreakEventValidate(BaseModel):
    validated: bool = True
