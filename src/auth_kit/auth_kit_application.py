from fastapi import FastAPI

from auth_kit.auth_kit_settings import AuthKitSettings
from auth_kit.auth_router import AuthRouter
from auth_kit.authentication_gateway import AuthenticationGateway
from auth_kit.database_factory import DatabaseFactory
from auth_kit.session_repository import SessionRepository
from auth_kit.user_directory import UserDirectory
from auth_kit.user_repository import UserRepository


class AuthKitApplication:
    def __init__(self, settings: AuthKitSettings | None = None, database: object | None = None) -> None:
        self._settings = settings or AuthKitSettings.from_env()
        self._database = database

    def create(self) -> FastAPI:
        database = self._database or DatabaseFactory().build(self._settings.database_url)
        users = UserRepository(database)
        users.initialize()
        sessions = SessionRepository(database)
        sessions.initialize()
        directory = UserDirectory(users, sessions)
        directory.ensure_bootstrap(self._settings.bootstrap_identifier, self._settings.bootstrap_password)
        gateway = AuthenticationGateway(users, sessions)
        app = FastAPI(title="Auth Kit", version="0.1.0")
        AuthRouter(gateway, directory).register(app)
        return app

    @staticmethod
    def create_default_app() -> FastAPI:
        return AuthKitApplication().create()
