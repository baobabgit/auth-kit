import httpx

from auth_kit.auth_http_client import AuthHttpClient
from auth_kit.auth_unavailable_error import AuthUnavailableError
from auth_kit.create_user_request import CreateUserRequest
from auth_kit.duplicate_identifier_error import DuplicateIdentifierError
from auth_kit.forbidden_error import ForbiddenError
from auth_kit.invalid_credentials_error import InvalidCredentialsError
from auth_kit.last_administrator_error import LastAdministratorError
from auth_kit.unauthorized_error import UnauthorizedError
from auth_kit.update_user_request import UpdateUserRequest
from auth_kit.user_not_found_error import UserNotFoundError
from auth_kit.role import Role


class TestAuthHttpClient:
    def test_success_and_errors(self) -> None:
        user = {
            "id": "1",
            "identifier": "admin",
            "role": "administrator",
            "active": True,
            "created_at": "t",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            path = request.url.path
            if path == "/health":
                return httpx.Response(200, json={"status": "ok", "service": "auth"})
            if path == "/login":
                return httpx.Response(200, json={"token": "tok", "user": user})
            if path == "/logout":
                return httpx.Response(204)
            if path == "/me":
                return httpx.Response(200, json=user)
            if path == "/users" and request.method == "GET":
                return httpx.Response(200, json={"items": [user]})
            if path == "/users" and request.method == "POST":
                return httpx.Response(200, json=user)
            if path.startswith("/users/") and request.method == "PATCH":
                return httpx.Response(200, json=user)
            return httpx.Response(404)

        client = AuthHttpClient("http://auth", transport=httpx.MockTransport(handler))
        assert client.health().service == "auth"
        assert client.login("admin", "x").token == "tok"
        client.logout("tok")
        assert client.me("tok").identifier == "admin"
        assert client.list_users("tok").items[0].id == "1"
        assert client.create_user("tok", CreateUserRequest(identifier="a", password="p")).id == "1"
        assert client.update_user("tok", "1", UpdateUserRequest(role=Role.USAGER)).id == "1"
        client.close()

        def errors(request: httpx.Request) -> httpx.Response:
            token = request.headers.get("authorization", "").split(" ")[-1]
            if token == "badlogin":
                return httpx.Response(401, text="incorrect")
            if token == "unauth":
                return httpx.Response(401, text="no")
            if token == "forbid":
                return httpx.Response(403, text="no")
            if token == "missing":
                return httpx.Response(404, text="no")
            if token == "last":
                return httpx.Response(409, text="Impossible de retirer le dernier administrateur.")
            if token == "dup":
                return httpx.Response(409, text="Identifiant déjà utilisé")
            if token == "crash":
                return httpx.Response(500, text="x")
            if token == "bad":
                return httpx.Response(400, text="no")
            raise httpx.ConnectError("offline", request=request)

        failing = AuthHttpClient("http://auth", transport=httpx.MockTransport(errors))
        try:
            failing.me("badlogin")
            raise AssertionError("expected")
        except InvalidCredentialsError:
            pass
        try:
            failing.me("unauth")
            raise AssertionError("expected")
        except UnauthorizedError:
            pass
        try:
            failing.me("forbid")
            raise AssertionError("expected")
        except ForbiddenError:
            pass
        try:
            failing.me("missing")
            raise AssertionError("expected")
        except UserNotFoundError:
            pass
        try:
            failing.me("last")
            raise AssertionError("expected")
        except LastAdministratorError:
            pass
        try:
            failing.me("dup")
            raise AssertionError("expected")
        except DuplicateIdentifierError:
            pass
        try:
            failing.me("crash")
            raise AssertionError("expected")
        except AuthUnavailableError:
            pass
        try:
            failing.me("bad")
            raise AssertionError("expected")
        except AuthUnavailableError:
            pass
        try:
            failing.me("offline")
            raise AssertionError("expected")
        except AuthUnavailableError:
            pass
        failing.close()
