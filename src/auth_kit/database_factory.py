from auth_kit.postgres_database import PostgresDatabase
from auth_kit.sqlite_database import SqliteDatabase


class DatabaseFactory:
    def build(self, target: str) -> SqliteDatabase | PostgresDatabase:
        if target.startswith("postgres://") or target.startswith("postgresql://"):
            return PostgresDatabase(target)
        return SqliteDatabase(target)
