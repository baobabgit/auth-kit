from pydantic import BaseModel, Field

from auth_kit.role import Role


class UserDocument(BaseModel):
    id: str
    identifier: str = Field(min_length=1)
    role: Role
    active: bool
    created_at: str

    def is_administrator(self) -> bool:
        return self.role.is_administrator()
