from pydantic import BaseModel, ConfigDict

class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    contribution_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: str
