from pydantic import BaseModel


class CropRead(BaseModel):
    id: str
    name: str
    aliases: list[str]
    category: str
    stages: list[str]
