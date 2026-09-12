class LastAdministratorError(Exception):
    def __init__(self) -> None:
        super().__init__("Impossible de retirer le dernier administrateur.")
