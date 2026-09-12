from auth_kit.invalid_credentials_error import InvalidCredentialsError
from auth_kit.password_hasher import PasswordHasher
from auth_kit.session_document import SessionDocument
from auth_kit.session_repository import SessionRepository
from auth_kit.token_factory import TokenFactory
from auth_kit.unauthorized_error import UnauthorizedError
from auth_kit.user_document import UserDocument
from auth_kit.user_repository import UserRepository


class AuthenticationGateway:
    def __init__(
        self,
        users: UserRepository,
        sessions: SessionRepository,
        hasher: PasswordHasher | None = None,
        tokens: TokenFactory | None = None,
    ) -> None:
        self._users = users
        self._sessions = sessions
        self._hasher = hasher or PasswordHasher()
        self._tokens = tokens or TokenFactory()

    def login(self, identifier: str, password: str) -> SessionDocument:
        record = self._users.find_by_identifier(identifier.strip())
        if record is None or not record.active or not self._hasher.verify(password, record.password_hash):
            raise InvalidCredentialsError()
        token = self._tokens.generate()
        self._sessions.create(self._tokens.digest(token), record.user_id)
        return SessionDocument(token=token, user=record.to_document())

    def logout(self, token: str) -> None:
        self._sessions.delete(self._tokens.digest(token))

    def current_user(self, token: str | None) -> UserDocument:
        if not token:
            raise UnauthorizedError()
        user_id = self._sessions.user_id_for(self._tokens.digest(token))
        if user_id is None:
            raise UnauthorizedError()
        record = self._users.get(user_id)
        if record is None or not record.active:
            raise UnauthorizedError()
        return record.to_document()
