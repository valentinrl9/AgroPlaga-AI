from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CountItem(BaseModel):
    name: str
    count: int


class TimelinePoint(BaseModel):
    date: str
    count: int


class FarmBreakdownItem(BaseModel):
    farm_id: int
    name: str
    crop: str
    farm_type: str
    scan_count: int


class UserAnalyticsSummary(BaseModel):
    days: int
    total_scans: int
    high_severity_count: int
    crops: list[CountItem]
    plagues: list[CountItem]


class ZoneContext(BaseModel):
    zone_id: int
    zone_name: str
    sigpac_code: str
    events_recent: int
    top_plague: str | None
    top_plague_count: int


class RecommendationResponse(BaseModel):
    plague: str
    crop: str
    severity: str
    severity_level: int
    urgency: str
    recommendation: str
    prevention_tip: str


class ScanHistoryItem(BaseModel):
    id: int
    crop: str
    plague: str
    confidence: float
    severity: str
    location: str | None = None
    farm_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonalAnalyticsResponse(BaseModel):
    summary: UserAnalyticsSummary
    timeline: list[TimelinePoint]
    farms: list[FarmBreakdownItem]
    recent_scans: list[ScanHistoryItem]
