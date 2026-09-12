from auth_kit.postgres_database import PostgresDatabase
from auth_kit.postgres_session import PostgresSession


class TestPostgresDatabase:
    def test_connect(self, monkeypatch) -> None:
        class FakeConnection:
            pass

        def fake_connect(dsn: str, row_factory: object = None) -> FakeConnection:
            assert dsn.startswith("postgresql://")
            return FakeConnection()

        monkeypatch.setattr("auth_kit.postgres_database.psycopg.connect", fake_connect)
        database = PostgresDatabase("postgresql://auth:auth@postgres:5432/auth")
        session = database.connect()
        assert isinstance(session, PostgresSession)
        assert database.dsn.startswith("postgresql://")
