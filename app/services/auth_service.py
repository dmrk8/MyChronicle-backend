import logging
from app.models.auth_models import LoginRequest, AuthResponse
from app.auth.jwt_handler import JWTHandler
from app.services.user_service import UserService
from dotenv import load_dotenv

load_dotenv()


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

            claims = self.jwt_handler.generate_claims(user.username)
            access_token = self.jwt_handler.create_access_token(claims)
            return AuthResponse(
                message="Login successful",
                access_token=access_token,
            )

        except ValueError as ve:
            logger.error(f"Login failed: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise ValueError(f"Authentication failed: {str(e)}")

   