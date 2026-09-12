class UnauthorizedError(Exception):
    def __init__(self) -> None:
        super().__init__("Authentification requise.")
