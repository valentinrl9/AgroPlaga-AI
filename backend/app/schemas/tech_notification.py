from datetime import datetime

from pydantic import BaseModel


class TechNotificationRead(BaseModel):
    id: int
    scan_id: int
    notification_type: str
    title: str
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TechNotificationUnreadCount(BaseModel):
    unread_count: int
    pending_scans: int
