from pydantic import BaseModel, Field

from auth_kit.role import Role


class CreateUserRequest(BaseModel):
    identifier: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: Role = Role.USAGER
