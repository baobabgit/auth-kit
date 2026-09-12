from pydantic import BaseModel, Field

from auth_kit.user_document import UserDocument


class UserListDocument(BaseModel):
    items: list[UserDocument] = Field(default_factory=list)
