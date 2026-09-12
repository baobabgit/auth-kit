import hashlib
import secrets


class TokenFactory:
    def generate(self) -> str:
        return secrets.token_urlsafe(32)

    def digest(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
