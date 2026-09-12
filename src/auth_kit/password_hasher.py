import hashlib
import os


class PasswordHasher:
    def hash(self, password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return f"{salt.hex()}${digest.hex()}"

    def verify(self, password: str, stored: str) -> bool:
        try:
            salt_hex, digest_hex = stored.split("$", 1)
        except ValueError:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            120_000,
        )
        return candidate.hex() == digest_hex
