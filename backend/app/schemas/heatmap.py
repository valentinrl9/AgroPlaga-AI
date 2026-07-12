from pydantic import BaseModel, Field


class HeatmapCellRead(BaseModel):
    zone_id: int
    sigpac_code: str
    zone_name: str
    lat: float
    lon: float
    count: int
    max_severity: int
    intensity: float = Field(ge=0.0, le=1.0)
    validated_count: int = 0
    pending_count: int = 0


class HeatmapResponse(BaseModel):
    hours: int
    min_severity: int
    plague: str | None
    cells: list[HeatmapCellRead]
