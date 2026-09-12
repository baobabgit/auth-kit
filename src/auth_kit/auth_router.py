from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response

from auth_kit.authentication_gateway import AuthenticationGateway
from auth_kit.create_user_request import CreateUserRequest
from auth_kit.duplicate_identifier_error import DuplicateIdentifierError
from auth_kit.forbidden_error import ForbiddenError
from auth_kit.invalid_credentials_error import InvalidCredentialsError
from auth_kit.last_administrator_error import LastAdministratorError
from auth_kit.login_request import LoginRequest
from auth_kit.session_document import SessionDocument
from auth_kit.unauthorized_error import UnauthorizedError
from auth_kit.update_user_request import UpdateUserRequest
from auth_kit.user_directory import UserDirectory
from auth_kit.user_document import UserDocument
from auth_kit.user_list_document import UserListDocument
from auth_kit.health_status import HealthStatus
from auth_kit.user_not_found_error import UserNotFoundError


class AuthRouter:
    def __init__(self, gateway: AuthenticationGateway, directory: UserDirectory) -> None:
        self._gateway = gateway
        self._directory = directory

    def register(self, app: FastAPI) -> None:
        app.add_api_route("/health", self.health, methods=["GET"], response_model=HealthStatus)
        app.add_api_route("/login", self.login, methods=["POST"], response_model=SessionDocument)
        app.add_api_route("/logout", self.logout, methods=["POST"])
        app.add_api_route("/me", self.me, methods=["GET"], response_model=UserDocument)
        app.add_api_route("/users", self.list_users, methods=["GET"], response_model=UserListDocument)
        app.add_api_route("/users", self.create_user, methods=["POST"], response_model=UserDocument)
        app.add_api_route("/users/{user_id}", self.update_user, methods=["PATCH"], response_model=UserDocument)

    def health(self) -> HealthStatus:
        return HealthStatus(status="ok", service="auth")

    def login(self, request: LoginRequest) -> SessionDocument:
        try:
            return self._gateway.login(request.identifier, request.password)
        except InvalidCredentialsError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    def logout(self, authorization: str | None = Header(default=None)) -> Response:
        token = self._bearer(authorization, required=False)
        if token:
            self._gateway.logout(token)
        return Response(status_code=204)

    def me(self, authorization: str | None = Header(default=None)) -> UserDocument:
        return self._actor(authorization)

    def list_users(self, authorization: str | None = Header(default=None)) -> UserListDocument:
        actor = self._actor(authorization)
        try:
            return UserListDocument(items=self._directory.list_users(actor))
        except ForbiddenError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    def create_user(self, request: CreateUserRequest, authorization: str | None = Header(default=None)) -> UserDocument:
        actor = self._actor(authorization)
        try:
            return self._directory.create_user(actor, request)
        except ForbiddenError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except DuplicateIdentifierError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def update_user(
        self,
        user_id: str,
        request: UpdateUserRequest,
        authorization: str | None = Header(default=None),
    ) -> UserDocument:
        actor = self._actor(authorization)
        try:
            return self._directory.update_user(actor, user_id, request)
        except ForbiddenError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except UserNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except LastAdministratorError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def _actor(self, authorization: str | None) -> UserDocument:
        try:
            return self._gateway.current_user(self._bearer(authorization, required=True))
        except UnauthorizedError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    def _bearer(self, authorization: str | None, required: bool) -> str | None:
        if not authorization:
            if required:
                raise HTTPException(status_code=401, detail="Authentification requise.")
            return None
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            if required:
                raise HTTPException(status_code=401, detail="Authentification requise.")
            return None
        return token
