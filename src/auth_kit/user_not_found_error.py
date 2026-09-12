class UserNotFoundError(Exception):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"Usager introuvable: {user_id}")
        self.user_id = user_id
