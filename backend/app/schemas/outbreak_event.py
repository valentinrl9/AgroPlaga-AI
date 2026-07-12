from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SeverityLevel = Literal[1, 2, 3]
OutbreakStatus = Literal["pending", "validated", "rejected"]
ValidateAction = Literal["confirm", "correct", "reject"]


class OutbreakEventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plague: str = Field(..., min_length=2, max_length=50)
    severity: SeverityLevel
    zone_id: int
    model_version: str = Field(default="v0.0", max_length=10)
    source_scan_id: int | None = None

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
    status: OutbreakStatus = "pending"
    original_plague: str | None = None
    corrected_plague: str | None = None
    display_plague: str
    source_scan_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class OutbreakEventValidate(BaseModel):
    validated: bool | None = None
    action: ValidateAction | None = None
    corrected_plague: str | None = Field(default=None, max_length=50)
    corrected_severity: SeverityLevel | None = None

    @model_validator(mode="after")
    def normalize_action(self) -> "OutbreakEventValidate":
        if self.action is None and self.validated is not None:
            self.action = "confirm" if self.validated else "reject"
        if self.action is None:
            self.action = "confirm"
        return self

    @field_validator("corrected_plague")
    @classmethod
    def normalize_corrected_plague(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()
