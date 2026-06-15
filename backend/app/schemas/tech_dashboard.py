from datetime import datetime

from pydantic import BaseModel


class TechOverview(BaseModel):
    hours: int
    events_recent: int
    validated_recent: int
    validation_rate: float
    active_alerts: int
    active_zones: int


class ZoneComparisonCell(BaseModel):
    zone_id: int
    sigpac_code: str
    zone_name: str
    lat: float
    lon: float
    count: int
    max_severity: int
    intensity: float
    validated_count: int


class TimelinePoint(BaseModel):
    date: str
    count: int


class CriticalAlertItem(BaseModel):
    id: int
    zone_id: int
    zone_name: str | None
    plague: str
    alert_type: str
    description: str
    priority_score: float | None
    created_at: datetime


class TechDashboardResponse(BaseModel):
    overview: TechOverview
    zone_comparison: list[ZoneComparisonCell]
    timeline: list[TimelinePoint]
    critical_alerts: list[CriticalAlertItem]
