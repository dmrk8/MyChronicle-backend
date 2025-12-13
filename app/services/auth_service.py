from app.models.auth_models import LoginRequest, AuthResponse
from app.auth.jwt_handler import JWTHandler
from app.services.user_service import UserService
from app.models.user_models import UserCreate, UserDB


class AuthService:
    def __init__(self, jwt_handler: JWTHandler, user_service: UserService):
        self.jwt_handler = jwt_handler
        self.user_service = user_service

    def authenticate_user(self, user_login: LoginRequest) -> str:
        try:
            user = self.user_service.get_by_username(user_login.username)

            if not user or not self.jwt_handler.verify_password(
                user_login.password, user.hash_password
            ):
                raise ValueError("Invalid username or password")

            return self.jwt_handler.create_access_token(user.username)

        except Exception as e:
            raise ValueError(f"Authentication failed: {str(e)}")

    def create_user(self, user_create: UserCreate) -> AuthResponse:
        try:
            existing_user = self.user_service.get_by_username(user_create.username)
            if existing_user:
                raise ValueError("Username already exists")

            hash_password = self.jwt_handler.hash_password(user_create.password)

            user_db = UserDB(
                username=user_create.username,
                hash_password=hash_password,  # type: ignore
            )

            result = self.user_service.create_user(user_db)

            return AuthResponse(
                message="User created successfully",
                data={"user_id": result.user_id},
            )

        except Exception as e:
            raise ValueError(f"User creation failed: {str(e)}")
