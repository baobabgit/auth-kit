from auth_kit.password_hasher import PasswordHasher


class TestPasswordHasher:
    def test_roundtrip_and_invalid(self) -> None:
        hasher = PasswordHasher()
        stored = hasher.hash("secret")
        assert hasher.verify("secret", stored) is True
        assert hasher.verify("nope", stored) is False
        assert hasher.verify("secret", "not-a-hash") is False
