from pydantic import BaseModel, Field


class OfficialSourceRef(BaseModel):
    id: str
    kind: str
    kind_label: str
    issuer: str
    title: str
    url: str | None = None
    note: str | None = None


class OfficialSourcesResponse(BaseModel):
    plague: str
    crop: str | None = None
    context: str
    sources: list[OfficialSourceRef] = Field(default_factory=list)
