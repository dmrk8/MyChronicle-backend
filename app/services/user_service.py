import structlog
from typing import Optional
from app.repositories.user_repository import UserRepository
from app.models.user_models import UserDB, UserUpdateRequest, UserResponse, UserCreate
from app.auth.password_handler import PasswordHandler

logger = structlog.get_logger()


class UserService:
    def __init__(self, user_repository: UserRepository, password_handler: PasswordHandler):
        self.user_repository = user_repository
        self.password_handler = password_handler
        self.logger = logger.bind(service="UserService")

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        try:
            existing = await self.user_repository.get_by_username(user_create.username)
            if existing:
                raise ValueError("Username already exists")

            hash_password = self.password_handler.hash_password(user_create.password)

            user_db = UserDB(username=user_create.username, hashPassword=hash_password)
            result = await self.user_repository.create(user_db)

            self.logger.info("user_registered", user_id=str(result.inserted_id))

            return UserResponse(
                message="User Registered Successfully",
                user_id=str(result.inserted_id),  # type: ignore
                acknowledged=result.acknowledged,
            )

        except ValueError as ve:
            self.logger.error("validation_error_create_user", error=str(ve))
            raise
        except Exception as e:
            self.logger.error("unexpected_error_create_user", error=str(e))
            raise

    async def update_user(self, user_id: str, update_request: UserUpdateRequest) -> UserResponse:
        exists = await self.user_repository.get_by_id(user_id)

        if not exists:
            self.logger.warning("update_nonexisting_user", user_id=user_id)
            raise ValueError("Cannot update nonexisting user")

        data_dict = update_request.model_dump()
        update_data = {k: v for k, v in data_dict.items() if v is not None}

        result = await self.user_repository.update(user_id, update_data)
        self.logger.info(
            "user_updated",
            user_id=user_id,
            matched_count=result.matched_count,
            modified_count=result.modified_count,
        )

        return UserResponse(
            message="User updated successfully",
            user_id=user_id,  # type: ignore
            acknowledged=result.acknowledged,
        )

    async def delete_user(self, user_id: str) -> UserResponse:
        try:
            existing_user = await self.user_repository.get_by_id(user_id)
            if not existing_user:
                self.logger.warning("delete_failed_user_not_found", user_id=user_id)
                raise ValueError("User not found")

            result = await self.user_repository.delete(user_id)
            self.logger.info("user_deleted", user_id=user_id, deleted_count=result.deleted_count)

            return UserResponse(
                message="User deleted successfully",
                user_id=user_id,  # type: ignore
                acknowledged=result.acknowledged,
            )

        except ValueError as ve:
            self.logger.error("validation_error_delete_user", error=str(ve))
            raise
        except Exception as e:
            self.logger.error("unexpected_error_delete_user", error=str(e))
            raise

    async def get_by_username(self, username: str) -> Optional[UserDB]:
        try:
            user = await self.user_repository.get_by_username(username)
            if user:
                self.logger.info("user_retrieved_by_username", username=username)
                return user
            self.logger.info("user_not_found_by_username", username=username)
            return None
        except Exception as e:
            self.logger.error("error_get_by_username", username=username, error=str(e))
            raise

    async def get_by_id(self, user_id: str) -> Optional[UserDB]:
        try:
            user = await self.user_repository.get_by_id(user_id)
            if user:
                self.logger.info("user_retrieved_by_id", user_id=user_id)
                return user
            self.logger.info("user_not_found_by_id", user_id=user_id)
            return None
        except Exception as e:
            self.logger.error("error_get_by_id", user_id=user_id, error=str(e))
            raise

    async def verify_credentials(self, username: str, password: str) -> Optional[UserDB]:
        """
        Verify username and password combination.
        Returns user if credentials are valid, None otherwise.
        Used by AuthService for login.
        """
        try:
            user = await self.user_repository.get_by_username(username)

            if not user:
                self.logger.info("authentication_failed", reason="user_not_found")
                return None

            if not self.password_handler.verify_password(password, user.hash_password):
                self.logger.warning("authentication_failed", reason="invalid_password")
                return None

            self.logger.info("credentials_verified", user_id=user.id)
            return user

        except Exception as e:
            self.logger.error("error_verifying_credentials", error=str(e))
            raise
