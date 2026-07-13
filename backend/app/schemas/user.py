from pydantic import BaseModel, ConfigDict

class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    contribution_count: int = 0
    has_field_premium: bool = False
    has_climate_module: bool = False
    has_siex_module: bool = False
    has_siex_enterprise: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: str
