from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FarmType = Literal["farm", "greenhouse"]


class FarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    crop: str = Field(min_length=1, max_length=50)
    farm_type: FarmType = "farm"
    zone_id: int | None = None
    surface_m2: float | None = Field(default=None, gt=0)
    sigpac_code: str | None = Field(default=None, max_length=20)


class FarmUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    crop: str | None = Field(default=None, min_length=1, max_length=50)
    surface_m2: float | None = Field(default=None, gt=0)
    sigpac_code: str | None = Field(default=None, max_length=20)


class FarmRead(BaseModel):
    id: int
    name: str
    crop: str
    farm_type: str
    zone_id: int | None
    surface_m2: float | None = None
    sigpac_code: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
