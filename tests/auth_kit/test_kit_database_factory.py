from auth_kit.database_factory import DatabaseFactory
from auth_kit.postgres_database import PostgresDatabase
from auth_kit.sqlite_database import SqliteDatabase


class TestDatabaseFactory:
    def test_sqlite_and_postgres(self) -> None:
        factory = DatabaseFactory()
        sqlite = factory.build("data/auth.sqlite")
        assert isinstance(sqlite, SqliteDatabase)
        postgres = factory.build("postgresql://auth:auth@postgres:5432/auth")
        assert isinstance(postgres, PostgresDatabase)
        postgres_alt = factory.build("postgres://auth:auth@postgres:5432/auth")
        assert isinstance(postgres_alt, PostgresDatabase)
