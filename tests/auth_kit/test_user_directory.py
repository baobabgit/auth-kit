from auth_kit.authentication_gateway import AuthenticationGateway
from auth_kit.create_user_request import CreateUserRequest
from auth_kit.duplicate_identifier_error import DuplicateIdentifierError
from auth_kit.forbidden_error import ForbiddenError
from auth_kit.invalid_credentials_error import InvalidCredentialsError
from auth_kit.last_administrator_error import LastAdministratorError
from auth_kit.password_hasher import PasswordHasher
from auth_kit.role import Role
from auth_kit.session_repository import SessionRepository
from auth_kit.unauthorized_error import UnauthorizedError
from auth_kit.update_user_request import UpdateUserRequest
from auth_kit.user_directory import UserDirectory
from auth_kit.user_not_found_error import UserNotFoundError
from auth_kit.user_repository import UserRepository
from auth_kit.sqlite_database import SqliteDatabase
from tests.support.temporary_database import TemporaryDatabase


class TestAuthPersistence:
    def test_login_directory_and_bootstrap(self) -> None:
        temp = TemporaryDatabase()
        try:
            database = SqliteDatabase(temp.path)
            users = UserRepository(database)
            users.initialize()
            sessions = SessionRepository(database)
            sessions.initialize()
            directory = UserDirectory(users, sessions)
            gateway = AuthenticationGateway(users, sessions)
            first = directory.ensure_bootstrap("admin", "secret")
            assert first is not None
            assert directory.ensure_bootstrap("admin", "secret") is None
            session = gateway.login("Admin", "secret")
            assert session.user.identifier == "admin"
            assert gateway.current_user(session.token).id == first.id
            gateway.logout(session.token)
            try:
                gateway.current_user(session.token)
                raise AssertionError("expected")
            except UnauthorizedError:
                pass
            try:
                gateway.current_user(None)
                raise AssertionError("expected")
            except UnauthorizedError:
                pass
            try:
                gateway.login("admin", "bad")
                raise AssertionError("expected")
            except InvalidCredentialsError:
                pass
            try:
                gateway.login("ghost", "secret")
                raise AssertionError("expected")
            except InvalidCredentialsError:
                pass
            created = directory.create_user(
                first,
                CreateUserRequest(identifier="lea", password="pass", role=Role.USAGER),
            )
            try:
                directory.create_user(created, CreateUserRequest(identifier="x", password="p"))
                raise AssertionError("expected")
            except ForbiddenError:
                pass
            try:
                directory.list_users(created)
                raise AssertionError("expected")
            except ForbiddenError:
                pass
            listed = directory.list_users(first)
            assert len(listed) == 2
            try:
                directory.create_user(first, CreateUserRequest(identifier="LEA", password="p"))
                raise AssertionError("expected")
            except DuplicateIdentifierError:
                pass
            updated = directory.update_user(
                first,
                created.id,
                UpdateUserRequest(role=Role.ADMINISTRATOR, password="new"),
            )
            assert updated.role is Role.ADMINISTRATOR
            gateway.login("lea", "new")
            deactivated = directory.update_user(first, created.id, UpdateUserRequest(active=False))
            assert deactivated.active is False
            try:
                gateway.login("lea", "new")
                raise AssertionError("expected")
            except InvalidCredentialsError:
                pass
            revived = directory.update_user(first, created.id, UpdateUserRequest(active=True))
            assert revived.active is True
            demoted = directory.update_user(first, created.id, UpdateUserRequest(role=Role.USAGER))
            assert demoted.role is Role.USAGER
            try:
                directory.update_user(first, first.id, UpdateUserRequest(active=False))
                raise AssertionError("expected")
            except LastAdministratorError:
                pass
            try:
                directory.update_user(first, first.id, UpdateUserRequest(role=Role.USAGER))
                raise AssertionError("expected")
            except LastAdministratorError:
                pass
            kept = directory.update_user(first, first.id, UpdateUserRequest(role=Role.ADMINISTRATOR))
            assert kept.role is Role.ADMINISTRATOR
            try:
                directory.update_user(first, "missing", UpdateUserRequest(active=True))
                raise AssertionError("expected")
            except UserNotFoundError:
                pass
            hasher = PasswordHasher()
            assert hasher.verify("secret", users.get(first.id).password_hash)  # type: ignore[union-attr]
        finally:
            temp.cleanup()
