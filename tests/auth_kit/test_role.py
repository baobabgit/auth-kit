from auth_kit.role import Role
from auth_kit.user_document import UserDocument


class TestRole:
    def test_administrator_flag(self) -> None:
        assert Role.ADMINISTRATOR.is_administrator() is True
        assert Role.USAGER.is_administrator() is False
        admin = UserDocument(
            id="1",
            identifier="admin",
            role=Role.ADMINISTRATOR,
            active=True,
            created_at="t",
        )
        usager = admin.model_copy(update={"role": Role.USAGER, "identifier": "bob"})
        assert admin.is_administrator() is True
        assert usager.is_administrator() is False
