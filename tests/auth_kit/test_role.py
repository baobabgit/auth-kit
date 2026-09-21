from auth_kit.role import Role
from auth_kit.user_document import UserDocument


class TestRole:
    def test_administrator_flag(self) -> None:
        assert Role.ADMINISTRATOR.is_administrator() is True
        assert Role.USAGER.is_administrator() is False
        assert Role.ANALYSTE_NOMINATIF.is_administrator() is False
        admin = UserDocument(
            id="1",
            identifier="admin",
            role=Role.ADMINISTRATOR,
            active=True,
            created_at="t",
        )
        usager = admin.model_copy(update={"role": Role.USAGER, "identifier": "bob"})
        nominatif = admin.model_copy(
            update={"role": Role.ANALYSTE_NOMINATIF, "identifier": "lea"}
        )
        assert admin.is_administrator() is True
        assert usager.is_administrator() is False
        assert nominatif.is_administrator() is False

    def test_trois_roles_applicatifs(self) -> None:
        assert {role.value for role in Role} == {
            "administrator",
            "analyste_nominatif",
            "usager",
        }
        assert Role("analyste_nominatif") is Role.ANALYSTE_NOMINATIF
        assert Role.ANALYSTE_NOMINATIF.is_analyste_nominatif() is True
        assert Role.USAGER.is_analyste_nominatif() is False
        assert Role.ADMINISTRATOR.is_analyste_nominatif() is False
