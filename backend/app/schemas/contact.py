from datetime import datetime

from pydantic import BaseModel, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=200, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    role: str = Field(min_length=2, max_length=40)
    organization: str = Field(min_length=2, max_length=200)
    phone: str = Field(min_length=6, max_length=40)
    interest: str = Field(min_length=2, max_length=80)


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
