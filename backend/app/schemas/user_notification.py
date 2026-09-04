from datetime import datetime

from pydantic import BaseModel

from app.schemas.community import PilotCollectiveRead, WeeklyVigilanceRead


class UserNotificationRead(BaseModel):
    id: int
    notification_type: str
    section: str
    title: str
    body: str
    reference_type: str | None = None
    reference_id: int | None = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserNotificationUnreadCount(BaseModel):
    unread_count: int
    sections: dict[str, int]

class ActivitySummaryRead(BaseModel):
    unread_count: int
    sections: dict[str, int]
    weekly_vigilance: WeeklyVigilanceRead
    streak_weeks: int
    open_incidents_action_count: int
    pilot_collective: PilotCollectiveRead
