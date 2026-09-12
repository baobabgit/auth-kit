from pydantic import BaseModel

from auth_kit.role import Role


class UpdateUserRequest(BaseModel):
    role: Role | None = None
    active: bool | None = None
    password: str | None = None
