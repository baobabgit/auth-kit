from datetime import datetime, timezone


class SessionRepository:
    def __init__(self, database: object) -> None:
        self._database = database

    def initialize(self) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token_digest TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def create(self, token_digest: str, user_id: str) -> None:
        with self._database.connect() as connection:
            connection.execute(
                "INSERT INTO sessions (token_digest, user_id, created_at) VALUES (?, ?, ?)",
                (token_digest, user_id, datetime.now(timezone.utc).isoformat()),
            )
            connection.commit()

    def user_id_for(self, token_digest: str) -> str | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT user_id FROM sessions WHERE token_digest = ?",
                (token_digest,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)["user_id"]  # type: ignore[arg-type]

    def delete(self, token_digest: str) -> None:
        with self._database.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_digest = ?", (token_digest,))
            connection.commit()

    def delete_for_user(self, user_id: str) -> None:
        with self._database.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            connection.commit()
