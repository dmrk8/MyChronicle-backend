import structlog
from app.models.auth_models import LoginRequest
from app.auth.jwt_handler import JWTHandler
from app.services.user_service import UserService
from app.exceptions import AuthenticationError


logger = structlog.get_logger("auth_service")

class AuthService:
    def __init__(self, jwt_handler: JWTHandler, user_service: UserService):
        self.jwt_handler = jwt_handler
        self.user_service = user_service
        

    async def login(self, user_login: LoginRequest) -> str:
        try:
            user = await self.user_service.verify_credentials(
                user_login.username, user_login.password
            )

            if not user:
                raise AuthenticationError("Invalid username or password")

            logger.info("User logged in successfully", username=user.username)

            return self.jwt_handler.create_access_token(user.id) 
            

        except AuthenticationError as ae:
            logger.error("Login failed", error=str(ae), user_id=user_login.username)
            raise
        except Exception as e:
            logger.error(
                "Unexpected error during login", error=str(e), username=user_login.username
            )
            raise 
    
