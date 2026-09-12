from auth_kit.role import Role
from auth_kit.user_document import UserDocument


class UserRecord:
    def __init__(
        self,
        user_id: str,
        identifier: str,
        password_hash: str,
        role: Role,
        active: bool,
        created_at: str,
    ) -> None:
        self.user_id = user_id
        self.identifier = identifier
        self.password_hash = password_hash
        self.role = role
        self.active = active
        self.created_at = created_at

    def to_document(self) -> UserDocument:
        return UserDocument(
            id=self.user_id,
            identifier=self.identifier,
            role=self.role,
            active=self.active,
            created_at=self.created_at,
        )
