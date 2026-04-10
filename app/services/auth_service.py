import structlog

from app.auth.jwt_handler import JWTHandler
from app.models.auth_models import RegisterRequest
from app.services.user_service import UserService

logger = structlog.get_logger("auth_service")


class AuthService:
    def __init__(
        self,
        jwt_handler: JWTHandler,
        user_service: UserService,
    ):
        self.jwt_handler = jwt_handler
        self.user_service = user_service

    async def register(self, register_request: RegisterRequest) -> str:
        user = await self.user_service.create_user(
            register_request.username, register_request.password
        )
        return self.jwt_handler.create_access_token(user.id)

    async def login(self, username: str, password: str) -> str:
        user = await self.user_service.verify_credentials(username, password)
        logger.info("login_success", username=user.username)  # type: ignore
        return self.jwt_handler.create_access_token(user.id)  # type: ignore
