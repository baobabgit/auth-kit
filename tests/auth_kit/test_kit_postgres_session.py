from auth_kit.postgres_session import PostgresSession


class TestPostgresSession:
    def test_adapt_commit_and_rollback(self) -> None:
        class FakeConnection:
            def __init__(self) -> None:
                self.sql = ""
                self.params: object = None
                self.committed = False
                self.rolled_back = False
                self.closed = False

            def execute(self, sql: str, params: object = ()) -> str:
                self.sql = sql
                self.params = params
                return "cursor"

            def commit(self) -> None:
                self.committed = True

            def rollback(self) -> None:
                self.rolled_back = True

            def close(self) -> None:
                self.closed = True

        connection = FakeConnection()
        session = PostgresSession(connection)
        assert session.adapt("SELECT * FROM t WHERE id = ?") == "SELECT * FROM t WHERE id = %s"
        with session as active:
            assert active.execute("SELECT * FROM t WHERE id = ?", ("a",)) == "cursor"
            assert connection.sql == "SELECT * FROM t WHERE id = %s"
            assert connection.params == ("a",)
        assert connection.committed
        assert connection.closed

        failing = FakeConnection()
        try:
            with PostgresSession(failing):
                raise RuntimeError("boom")
        except RuntimeError:
            pass
        assert failing.rolled_back
        assert failing.closed
