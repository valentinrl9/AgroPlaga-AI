from datetime import datetime

from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=200, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    role: str = Field(min_length=2, max_length=40)
    message: str = Field(min_length=10, max_length=2000)


class ContactRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactAck(BaseModel):
    ok: bool = True
    message: str = "Mensaje recibido. Te contactaremos pronto."
