import psycopg
from psycopg.rows import dict_row

from auth_kit.postgres_session import PostgresSession


class PostgresDatabase:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def connect(self) -> PostgresSession:
        connection = psycopg.connect(self.dsn, row_factory=dict_row)
        return PostgresSession(connection)
