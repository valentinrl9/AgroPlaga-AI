from pydantic import BaseModel, Field


class NotificationPreferencesRead(BaseModel):
    push_scan_validation: bool = True
    push_incidents: bool = True
    push_carencia: bool = True
    push_alerts_comarcal: bool = False
    push_badges: bool = True
    push_weekly: bool = True
    push_tech_pending: bool = True
    quiet_hours_enabled: bool = True
    quiet_hours_start: int = Field(default=22, ge=0, le=23)
    quiet_hours_end: int = Field(default=7, ge=0, le=23)


class NotificationPreferencesUpdate(BaseModel):
    push_scan_validation: bool | None = None
    push_incidents: bool | None = None
    push_carencia: bool | None = None
    push_alerts_comarcal: bool | None = None
    push_badges: bool | None = None
    push_weekly: bool | None = None
    push_tech_pending: bool | None = None
    quiet_hours_enabled: bool | None = None
    quiet_hours_start: int | None = Field(default=None, ge=0, le=23)
    quiet_hours_end: int | None = Field(default=None, ge=0, le=23)
