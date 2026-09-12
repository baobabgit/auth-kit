import os


class AuthKitSettings:
    def __init__(
        self,
        database_url: str,
        bootstrap_identifier: str = "admin",
        bootstrap_password: str = "riftbound",
    ) -> None:
        self.database_url = database_url
        self.bootstrap_identifier = bootstrap_identifier
        self.bootstrap_password = bootstrap_password

    @classmethod
    def from_env(cls) -> "AuthKitSettings":
        url = os.environ.get("AUTH_DATABASE_URL")
        if not url:
            url = os.environ.get("AUTH_DATABASE_PATH", "data/auth.sqlite")
        return cls(
            database_url=url,
            bootstrap_identifier=os.environ.get("AUTH_BOOTSTRAP_IDENTIFIER", "admin"),
            bootstrap_password=os.environ.get("AUTH_BOOTSTRAP_PASSWORD", "riftbound"),
        )
