from pydantic import BaseModel, ConfigDict


class ZoneRead(BaseModel):
    id: int
    sigpac_code: str
    name: str
    province: str
    municipality_code: str
    lat: float
    lon: float

    model_config = ConfigDict(from_attributes=True)
