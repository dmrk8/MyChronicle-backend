import structlog

from app.auth.jwt_handler import JWTHandler
from app.core.exceptions import UnauthorizedException
from app.models.auth.auth_models import LoginRequest, RegisterRequest
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

    def create_access_token(self, user_id: str) -> str:
        claims = self.jwt_handler.generate_claims(user_id)
        return self.jwt_handler.encode_token(claims)

    def verify_token(self, token: str) -> str:
        """Verifies the JWT token and returns the user_id if valid

        Args:
            token (str): JWT token to verify

        Raises:
            AuthenticationError: if the token is invalid

        Returns:
            str: returns user_id if the token is valid
        """
        claims = self.jwt_handler.decode_token(token)

        if not claims or not claims.sub or not isinstance(claims.sub, str):
            raise UnauthorizedException("Invalid token")

        return claims.sub

    async def register(self, register_request: RegisterRequest) -> str:
        """Creates a new user and returns an access token

        Args:
            register_request (RegisterRequest): Request object containing username and password

        Returns:
            str: Access token for the newly created user
        """
        user = await self.user_service.create_user(
            register_request.username, register_request.password
        )
        return self.create_access_token(str(user.id))

    async def login(self, login_request: LoginRequest) -> str:
        user = await self.user_service.verify_credentials(
            login_request.username, login_request.password
        )
        if not user:
            raise UnauthorizedException("Invalid username or password")
        return self.create_access_token(str(user.id))
