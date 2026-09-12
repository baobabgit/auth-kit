from pydantic import BaseModel, Field

from auth_kit.user_document import UserDocument


class SessionDocument(BaseModel):
    token: str = Field(min_length=1)
    user: UserDocument
