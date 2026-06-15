from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FarmType = Literal["farm", "greenhouse"]


class FarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    crop: str = Field(min_length=1, max_length=50)
    farm_type: FarmType = "farm"
    zone_id: int | None = None


class FarmRead(BaseModel):
    id: int
    name: str
    crop: str
    farm_type: str
    zone_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
