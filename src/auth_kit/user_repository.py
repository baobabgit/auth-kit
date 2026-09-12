from datetime import datetime, timezone
from uuid import uuid4

from auth_kit.duplicate_identifier_error import DuplicateIdentifierError
from auth_kit.role import Role
from auth_kit.user_record import UserRecord


class UserRepository:
    def __init__(self, database: object) -> None:
        self._database = database

    def initialize(self) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    active INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def count(self) -> int:
        with self._database.connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS total FROM users").fetchone()
        return int(dict(row)["total"])  # type: ignore[arg-type]

    def count_active_administrators(self) -> int:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM users WHERE role = ? AND active = 1",
                (Role.ADMINISTRATOR.value,),
            ).fetchone()
        return int(dict(row)["total"])  # type: ignore[arg-type]

    def list_all(self) -> list[UserRecord]:
        with self._database.connect() as connection:
            rows = connection.execute("SELECT * FROM users ORDER BY identifier").fetchall()
        return [self._from_row(row) for row in rows]

    def get(self, user_id: str) -> UserRecord | None:
        with self._database.connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return None
        return self._from_row(row)

    def find_by_identifier(self, identifier: str) -> UserRecord | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE LOWER(identifier) = ?",
                (identifier.casefold(),),
            ).fetchone()
        if row is None:
            return None
        return self._from_row(row)

    def insert(self, identifier: str, password_hash: str, role: Role) -> UserRecord:
        if self.find_by_identifier(identifier) is not None:
            raise DuplicateIdentifierError(identifier)
        record = UserRecord(
            user_id=str(uuid4()),
            identifier=identifier.strip(),
            password_hash=password_hash,
            role=role,
            active=True,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO users (id, identifier, password_hash, role, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.user_id,
                    record.identifier,
                    record.password_hash,
                    record.role.value,
                    1,
                    record.created_at,
                ),
            )
            connection.commit()
        return record

    def update(self, record: UserRecord) -> UserRecord:
        with self._database.connect() as connection:
            connection.execute(
                """
                UPDATE users SET identifier = ?, password_hash = ?, role = ?, active = ?
                WHERE id = ?
                """,
                (
                    record.identifier,
                    record.password_hash,
                    record.role.value,
                    1 if record.active else 0,
                    record.user_id,
                ),
            )
            connection.commit()
        return record

    def _from_row(self, row: object) -> UserRecord:
        mapping = dict(row)  # type: ignore[arg-type]
        return UserRecord(
            user_id=mapping["id"],
            identifier=mapping["identifier"],
            password_hash=mapping["password_hash"],
            role=Role(mapping["role"]),
            active=bool(mapping["active"]),
            created_at=mapping["created_at"],
        )
