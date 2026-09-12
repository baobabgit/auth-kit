from auth_kit.health_status import HealthStatus


class TestHealthStatus:
    def test_fields(self) -> None:
        status = HealthStatus(status="ok", service="auth")
        assert status.status == "ok"
        assert status.service == "auth"
