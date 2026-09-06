from datetime import datetime

from pydantic import BaseModel, Field


class DeviceTokenRegister(BaseModel):
    token: str = Field(min_length=10, max_length=512)
    platform: str = Field(default="android", max_length=20)


class DeviceTokenRead(BaseModel):
    id: int
    platform: str
    updated_at: datetime

    model_config = {"from_attributes": True}
