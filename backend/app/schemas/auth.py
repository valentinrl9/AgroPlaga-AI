from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class UserLogin(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    invite_code: str | None = None
    consent_map_anonymous: bool = False

    @field_validator("consent_map_anonymous")
    @classmethod
    def require_map_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Debes aceptar el mapa anónimo para registrarte")
        return value
