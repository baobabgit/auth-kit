from pathlib import Path

from auth_kit.sqlite_database import SqliteDatabase


class TestSqliteDatabase:
    def test_creates_parent_and_connects(self, tmp_path: Path) -> None:
        path = tmp_path / "nested" / "db.sqlite"
        database = SqliteDatabase(str(path))
        connection = database.connect()
        try:
            connection.execute("CREATE TABLE t (id INTEGER)")
            connection.commit()
        finally:
            connection.close()
        assert path.exists()

    def test_memory_skips_mkdir(self) -> None:
        database = SqliteDatabase(":memory:")
        connection = database.connect()
        connection.close()
        assert database.path == ":memory:"

    def test_relative_path(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        database = SqliteDatabase("local.sqlite")
        connection = database.connect()
        connection.close()
