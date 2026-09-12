from auth_kit.auth_kit_settings import AuthKitSettings


class TestAuthKitSettings:
    def test_from_env_path(self, monkeypatch) -> None:
        monkeypatch.delenv("AUTH_DATABASE_URL", raising=False)
        monkeypatch.setenv("AUTH_DATABASE_PATH", "/tmp/a.sqlite")
        monkeypatch.setenv("AUTH_BOOTSTRAP_IDENTIFIER", "root")
        monkeypatch.setenv("AUTH_BOOTSTRAP_PASSWORD", "x")
        settings = AuthKitSettings.from_env()
        assert settings.database_url == "/tmp/a.sqlite"
        assert settings.bootstrap_identifier == "root"
        assert settings.bootstrap_password == "x"

    def test_from_env_url(self, monkeypatch) -> None:
        monkeypatch.setenv("AUTH_DATABASE_URL", "postgresql://riftbound:riftbound@postgres:5432/auth")
        settings = AuthKitSettings.from_env()
        assert settings.database_url.startswith("postgresql://")

    def test_defaults(self, monkeypatch) -> None:
        monkeypatch.delenv("AUTH_DATABASE_URL", raising=False)
        monkeypatch.delenv("AUTH_DATABASE_PATH", raising=False)
        monkeypatch.delenv("AUTH_BOOTSTRAP_IDENTIFIER", raising=False)
        monkeypatch.delenv("AUTH_BOOTSTRAP_PASSWORD", raising=False)
        settings = AuthKitSettings.from_env()
        assert settings.database_url.endswith("auth.sqlite")
        assert settings.bootstrap_identifier == "admin"
        assert settings.bootstrap_password == "riftbound"
