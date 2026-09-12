from auth_kit.token_factory import TokenFactory


class TestTokenFactory:
    def test_generate_and_digest(self) -> None:
        factory = TokenFactory()
        token = factory.generate()
        assert len(token) > 10
        assert factory.digest(token) != token
        assert factory.digest(token) == factory.digest(token)
