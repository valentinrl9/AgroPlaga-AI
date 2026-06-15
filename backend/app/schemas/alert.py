from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertRead(BaseModel):
    id: int
    zone_id: int
    zone_name: str | None = None
    plague: str
    alert_type: str
    description: str
    priority_score: float | None
    created_at: datetime
    active: bool

    model_config = ConfigDict(from_attributes=True)


class AlertDismiss(BaseModel):
    active: bool = False


class AlertPreferenceItem(BaseModel):
    plague: str = Field(min_length=1, max_length=50)
    enabled: bool = True


class AlertPreferencesUpdate(BaseModel):
    preferences: list[AlertPreferenceItem]


class AlertPreferencesRead(BaseModel):
    preferences: list[AlertPreferenceItem]
    available_plagues: list[str]
