from auth_kit.authentication_gateway import AuthenticationGateway
from auth_kit.password_hasher import PasswordHasher
from auth_kit.role import Role
from auth_kit.session_repository import SessionRepository
from auth_kit.unauthorized_error import UnauthorizedError
from auth_kit.user_repository import UserRepository
from auth_kit.sqlite_database import SqliteDatabase
from tests.support.temporary_database import TemporaryDatabase


class TestAuthenticationGateway:
    def test_inactive_or_missing_user_session(self) -> None:
        temp = TemporaryDatabase()
        try:
            database = SqliteDatabase(temp.path)
            users = UserRepository(database)
            users.initialize()
            sessions = SessionRepository(database)
            sessions.initialize()
            gateway = AuthenticationGateway(users, sessions)
            record = users.insert("bob", PasswordHasher().hash("pw"), Role.USAGER)
            session = gateway.login("bob", "pw")
            record.active = False
            users.update(record)
            try:
                gateway.current_user(session.token)
                raise AssertionError("expected")
            except UnauthorizedError:
                pass
            sessions.create("dead", "missing-user")
            try:
                AuthenticationGateway(users, sessions, tokens=_FixedTokens("raw", "dead")).current_user("raw")
                raise AssertionError("expected")
            except UnauthorizedError:
                pass
        finally:
            temp.cleanup()


class _FixedTokens:
    def __init__(self, raw: str, digest: str) -> None:
        self._raw = raw
        self._digest = digest

    def generate(self) -> str:
        return self._raw

    def digest(self, token: str) -> str:
        del token
        return self._digest
