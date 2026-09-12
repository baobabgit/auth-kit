from fastapi import FastAPI

from auth_kit.auth_kit_application import AuthKitApplication
from auth_kit.auth_kit_settings import AuthKitSettings
from auth_kit.sqlite_database import SqliteDatabase
from tests.support.temporary_database import TemporaryDatabase


class TestAuthKitApplication:
    def test_kit_builds_app(self, monkeypatch, tmp_path) -> None:
        temp = TemporaryDatabase()
        try:
            database = SqliteDatabase(temp.path)
            app = AuthKitApplication(AuthKitSettings(temp.path), database).create()
            assert isinstance(app, FastAPI)
            assert app.title == "Auth Kit"
        finally:
            temp.cleanup()
        monkeypatch.delenv("AUTH_DATABASE_URL", raising=False)
        monkeypatch.setenv("AUTH_DATABASE_PATH", str(tmp_path / "a.sqlite"))
        hosted = AuthKitApplication.create_default_app()
        assert hosted.title == "Auth Kit"
