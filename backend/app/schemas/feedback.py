from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    scan_id: int
    is_correct: bool
    corrected_plague: str | None = Field(default=None, max_length=50)
    comment: str | None = Field(default=None, max_length=500)


class FeedbackRead(BaseModel):
    id: int
    scan_id: int
    user_id: int | None
    is_correct: bool | None
    corrected_plague: str | None
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
