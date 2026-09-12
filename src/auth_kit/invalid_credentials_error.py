class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Identifiant ou mot de passe incorrect.")
