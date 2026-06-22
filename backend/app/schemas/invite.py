from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PilotInviteCreate(BaseModel):
    code: str = Field(min_length=6, max_length=32)
    role: str = "farmer"
    label: str | None = Field(default=None, max_length=120)
    max_uses: int = Field(default=1, ge=1, le=100)
    expires_at: datetime | None = None


class PilotInviteRead(BaseModel):
    id: int
    code: str
    role: str
    label: str | None
    max_uses: int
    uses_count: int
    expires_at: datetime | None
    revoked: bool
    created_at: datetime
    redeemed_by_user_id: int | None

    model_config = ConfigDict(from_attributes=True)


class AdminUserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    contribution_count: int

    model_config = ConfigDict(from_attributes=True)
