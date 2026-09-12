from typing import Any

import httpx

from auth_kit.auth_unavailable_error import AuthUnavailableError
from auth_kit.create_user_request import CreateUserRequest
from auth_kit.duplicate_identifier_error import DuplicateIdentifierError
from auth_kit.forbidden_error import ForbiddenError
from auth_kit.invalid_credentials_error import InvalidCredentialsError
from auth_kit.last_administrator_error import LastAdministratorError
from auth_kit.login_request import LoginRequest
from auth_kit.session_document import SessionDocument
from auth_kit.unauthorized_error import UnauthorizedError
from auth_kit.update_user_request import UpdateUserRequest
from auth_kit.health_status import HealthStatus
from auth_kit.user_document import UserDocument
from auth_kit.user_list_document import UserListDocument
from auth_kit.user_not_found_error import UserNotFoundError


class AuthHttpClient:
    def __init__(self, base_url: str, transport: httpx.BaseTransport | None = None) -> None:
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=10.0, transport=transport)

    def close(self) -> None:
        self._client.close()

    def health(self) -> HealthStatus:
        return HealthStatus.model_validate(self._get("/health"))

    def login(self, identifier: str, password: str) -> SessionDocument:
        payload = self._request(
            "POST",
            "/login",
            json=LoginRequest(identifier=identifier, password=password).model_dump(),
        )
        return SessionDocument.model_validate(payload)

    def logout(self, token: str) -> None:
        self._request("POST", "/logout", headers=self._headers(token))

    def me(self, token: str) -> UserDocument:
        return UserDocument.model_validate(self._get("/me", headers=self._headers(token)))

    def list_users(self, token: str) -> UserListDocument:
        return UserListDocument.model_validate(self._get("/users", headers=self._headers(token)))

    def create_user(self, token: str, request: CreateUserRequest) -> UserDocument:
        payload = self._request("POST", "/users", json=request.model_dump(mode="json"), headers=self._headers(token))
        return UserDocument.model_validate(payload)

    def update_user(self, token: str, user_id: str, request: UpdateUserRequest) -> UserDocument:
        payload = self._request(
            "PATCH",
            f"/users/{user_id}",
            json=request.model_dump(mode="json", exclude_none=True),
            headers=self._headers(token),
        )
        return UserDocument.model_validate(payload)

    def _headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def _get(self, path: str, headers: dict[str, str] | None = None) -> Any:
        return self._request("GET", path, headers=headers)

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.RequestError as exc:
            raise AuthUnavailableError(str(exc)) from exc
        if response.status_code == 401:
            detail = response.text
            if "incorrect" in detail:
                raise InvalidCredentialsError()
            raise UnauthorizedError()
        if response.status_code == 403:
            raise ForbiddenError()
        if response.status_code == 404:
            raise UserNotFoundError(path.rsplit("/", 1)[-1])
        if response.status_code == 409:
            if "administrateur" in response.text:
                raise LastAdministratorError()
            raise DuplicateIdentifierError(path)
        if response.status_code >= 500:
            raise AuthUnavailableError(f"Service d'authentification en erreur ({response.status_code}).")
        if response.status_code >= 400:
            raise AuthUnavailableError(response.text)
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()
