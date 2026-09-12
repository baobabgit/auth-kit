from pathlib import Path
import sqlite3


class SqliteDatabase:
    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_parent()

    def _ensure_parent(self) -> None:
        if self.path == ":memory:":
            return
        parent = Path(self.path).parent
        if str(parent) not in {"", "."}:
            parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
