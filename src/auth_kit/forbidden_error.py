class ForbiddenError(Exception):
    def __init__(self, message: str = "Droits insuffisants.") -> None:
        super().__init__(message)
        self.message = message
