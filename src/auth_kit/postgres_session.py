class PostgresSession:
    def __init__(self, connection: object) -> None:
        self._connection = connection

    def execute(self, sql: str, params: tuple | list = ()) -> object:
        return self._connection.execute(self.adapt(sql), params)  # type: ignore[union-attr]

    def adapt(self, sql: str) -> str:
        return sql.replace("?", "%s")

    def commit(self) -> None:
        self._connection.commit()  # type: ignore[union-attr]

    def rollback(self) -> None:
        self._connection.rollback()  # type: ignore[union-attr]

    def close(self) -> None:
        self._connection.close()  # type: ignore[union-attr]

    def __enter__(self) -> "PostgresSession":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
