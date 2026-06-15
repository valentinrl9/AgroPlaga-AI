from datetime import datetime

from pydantic import BaseModel


class BadgeRead(BaseModel):
    code: str
    label: str
    earned_at: datetime


class ZoneRankingEntry(BaseModel):
    zone_id: int
    zone_name: str
    contributions: int
    validated_count: int


class WeeklyVigilanceRead(BaseModel):
    goal: int
    current: int
    completed: bool
    ends_at: datetime
    description: str


class CommunityProfileRead(BaseModel):
    contribution_count: int
    badges: list[BadgeRead]
    weekly_vigilance: WeeklyVigilanceRead
    zone_ranking: list[ZoneRankingEntry]
