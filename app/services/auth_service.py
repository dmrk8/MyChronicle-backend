import logging
from app.models.auth_models import LoginRequest, AuthResponse, RefreshTokenRequest
from app.auth.jwt_handler import JWTHandler
from app.services.user_service import UserService


logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, jwt_handler: JWTHandler, user_service: UserService):
        self.jwt_handler = jwt_handler
        self.user_service = user_service

    async def login(self, user_login: LoginRequest) -> AuthResponse:
        try:
            user = await self.user_service.verify_credentials(
                user_login.username, user_login.password
            )

            if not user:
                raise ValueError("Invalid username or password")

            logger.info(f"User {user.username} logged in successfully")

            access_token = self.jwt_handler.create_access_token(user.username)
            refresh_token = self.jwt_handler.create_refresh_token(
                user.username, user_login.is_remember_me
            )

            return AuthResponse(
                message="Login successful",
                access_token=access_token,  # type: ignore
                refresh_token=refresh_token,  # type: ignore
            )

        except ValueError as ve:
            logger.error(f"Login failed: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise ValueError(f"Authentication failed: {str(e)}")

    async def refresh_access_token(self, refresh_request: RefreshTokenRequest) -> AuthResponse:
        username = self.jwt_handler.verify_token(
            refresh_request.refresh_token, expected_type="refresh"
        )
        if not username:
            raise ValueError("Invalid or expired refresh token")

        access_token = self.jwt_handler.create_access_token(username)

        return AuthResponse(
            message="Token refreshed",
            access_token=access_token,  # type: ignore
            refresh_token=refresh_request.refresh_token,  # type: ignore
        )
        
    