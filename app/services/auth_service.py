import structlog
from app.models.auth_models import LoginRequest, AuthResponse, RefreshTokenRequest
from app.auth.jwt_handler import JWTHandler
from app.services.user_service import UserService
from app.exceptions import AuthenticationError, TokenError


logger = structlog.get_logger()


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
                raise AuthenticationError("Invalid username or password")

            logger.info("User logged in successfully", username=user.username)

            access_token = self.jwt_handler.create_access_token(user.id) # type: ignore
            refresh_token = self.jwt_handler.create_refresh_token(
                user.username, user_login.is_remember_me
            )

            await self.jwt_handler.store_refresh_token(user.id, refresh_token, user_login.is_remember_me)  # type: ignore
            return AuthResponse(
                message="Login successful",
                access_token=access_token,  # type: ignore
                refresh_token=refresh_token,  # type: ignore
            )

        except AuthenticationError as ae:
            logger.error("Login failed", error=str(ae), user_id=user_login.username)
            raise
        except Exception as e:
            logger.error("Unexpected error during login", error=str(e), username=user_login.username)
            raise ValueError(f"Authentication failed: {str(e)}")
    
    
    #HANDLE THIS
    async def refresh_access_token(self, refresh_request: RefreshTokenRequest) -> AuthResponse:
        user_id = self.jwt_handler.verify_token(
            refresh_request.refresh_token, expected_type="refresh"
        )
        if not user_id:
            raise ValueError("Invalid or expired refresh token")

        access_token = self.jwt_handler.create_access_token(user_id)

        return AuthResponse(
            message="Token refreshed",
            access_token=access_token,  # type: ignore
            refresh_token=refresh_request.refresh_token,  # type: ignore
        )
        
    async def logout(self, user_id: str):
        await self.jwt_handler.revoke_refresh_token(user_id)
