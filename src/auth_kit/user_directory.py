from auth_kit.create_user_request import CreateUserRequest
from auth_kit.forbidden_error import ForbiddenError
from auth_kit.last_administrator_error import LastAdministratorError
from auth_kit.password_hasher import PasswordHasher
from auth_kit.role import Role
from auth_kit.session_repository import SessionRepository
from auth_kit.update_user_request import UpdateUserRequest
from auth_kit.user_document import UserDocument
from auth_kit.user_not_found_error import UserNotFoundError
from auth_kit.user_record import UserRecord
from auth_kit.user_repository import UserRepository


class UserDirectory:
    def __init__(
        self,
        users: UserRepository,
        sessions: SessionRepository,
        hasher: PasswordHasher | None = None,
    ) -> None:
        self._users = users
        self._sessions = sessions
        self._hasher = hasher or PasswordHasher()

    def ensure_bootstrap(self, identifier: str, password: str) -> UserDocument | None:
        if self._users.count() > 0:
            return None
        record = self._users.insert(identifier, self._hasher.hash(password), Role.ADMINISTRATOR)
        return record.to_document()

    def list_users(self, actor: UserDocument) -> list[UserDocument]:
        self._require_admin(actor)
        return [record.to_document() for record in self._users.list_all()]

    def create_user(self, actor: UserDocument, request: CreateUserRequest) -> UserDocument:
        self._require_admin(actor)
        record = self._users.insert(request.identifier.strip(), self._hasher.hash(request.password), request.role)
        return record.to_document()

    def update_user(self, actor: UserDocument, user_id: str, request: UpdateUserRequest) -> UserDocument:
        self._require_admin(actor)
        record = self._require(user_id)
        if request.role is not None:
            self._guard_last_admin(record, new_role=request.role, new_active=record.active)
            record.role = request.role
        if request.active is not None:
            self._guard_last_admin(record, new_role=record.role, new_active=request.active)
            record.active = request.active
            if not record.active:
                self._sessions.delete_for_user(record.user_id)
        if request.password:
            record.password_hash = self._hasher.hash(request.password)
        return self._users.update(record).to_document()

    def _require(self, user_id: str) -> UserRecord:
        record = self._users.get(user_id)
        if record is None:
            raise UserNotFoundError(user_id)
        return record

    def _require_admin(self, actor: UserDocument) -> None:
        if not actor.is_administrator():
            raise ForbiddenError("Réservé aux administrateurs.")

    def _guard_last_admin(self, record: UserRecord, new_role: Role, new_active: bool) -> None:
        if record.role is not Role.ADMINISTRATOR or not record.active:
            return
        loses_admin = new_role is not Role.ADMINISTRATOR or not new_active
        if loses_admin and self._users.count_active_administrators() <= 1:
            raise LastAdministratorError()
