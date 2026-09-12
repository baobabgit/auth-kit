class DuplicateIdentifierError(Exception):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Identifiant déjà utilisé: {identifier}")
        self.identifier = identifier
