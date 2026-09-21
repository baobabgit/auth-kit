from fastapi.testclient import TestClient

from auth_kit.auth_kit_application import AuthKitApplication
from auth_kit.auth_kit_settings import AuthKitSettings
from tests.support.temporary_database import TemporaryDatabase


class TestAuthRouter:
    def test_api(self) -> None:
        temp = TemporaryDatabase()
        try:
            app = AuthKitApplication(AuthKitSettings(temp.path, "admin", "secret")).create()
            client = TestClient(app)
            assert client.get("/health").json()["service"] == "auth"
            assert client.post("/login", json={"identifier": "admin", "password": "nope"}).status_code == 401
            session = client.post("/login", json={"identifier": "admin", "password": "secret"})
            token = session.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}
            me = client.get("/me", headers=headers)
            assert me.json()["identifier"] == "admin"
            assert client.get("/me").status_code == 401
            assert client.get("/me", headers={"Authorization": "Basic x"}).status_code == 401
            assert client.get("/me", headers={"Authorization": "Bearer"}).status_code == 401
            assert client.get("/me", headers={"Authorization": "Bearer nope"}).status_code == 401
            created = client.post(
                "/users",
                headers=headers,
                json={"identifier": "lea", "password": "pass", "role": "usager"},
            )
            lea_id = created.json()["id"]
            nominatif = client.post(
                "/users",
                headers=headers,
                json={
                    "identifier": "marc",
                    "password": "pass",
                    "role": "analyste_nominatif",
                },
            )
            assert nominatif.status_code == 200
            assert nominatif.json()["role"] == "analyste_nominatif"
            marc_session = client.post(
                "/login", json={"identifier": "marc", "password": "pass"}
            )
            marc_headers = {
                "Authorization": f"Bearer {marc_session.json()['token']}"
            }
            assert client.get("/users", headers=marc_headers).status_code == 403
            assert client.get("/users", headers=headers).status_code == 200
            assert client.post(
                "/users",
                headers=headers,
                json={"identifier": "lea", "password": "pass", "role": "usager"},
            ).status_code == 409
            lea_session = client.post("/login", json={"identifier": "lea", "password": "pass"})
            lea_headers = {"Authorization": f"Bearer {lea_session.json()['token']}"}
            assert client.get("/users", headers=lea_headers).status_code == 403
            assert client.post(
                "/users",
                headers=lea_headers,
                json={"identifier": "x", "password": "p", "role": "usager"},
            ).status_code == 403
            assert client.patch(
                f"/users/{lea_id}",
                headers=lea_headers,
                json={"active": False},
            ).status_code == 403
            assert client.patch("/users/missing", headers=headers, json={"active": True}).status_code == 404
            assert client.patch(
                f"/users/{me.json()['id']}",
                headers=headers,
                json={"active": False},
            ).status_code == 409
            patched = client.patch(
                f"/users/{lea_id}",
                headers=headers,
                json={"role": "administrator", "password": "pass2"},
            )
            assert patched.json()["role"] == "administrator"
            assert client.post("/logout", headers=headers).status_code == 204
            assert client.get("/me", headers=headers).status_code == 401
            assert client.post("/logout").status_code == 204
            assert client.post("/logout", headers={"Authorization": "Bearer"}).status_code == 204
        finally:
            temp.cleanup()
