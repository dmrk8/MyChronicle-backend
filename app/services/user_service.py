import structlog
from typing import Optional
from app.repositories.user_repository import UserRepository
from app.models.user_models import (
    UserDB,
    UserInsert,
    User,
    UserUpdateRequest,
    UserCreate,
)
from app.auth.password_handler import PasswordHandler
from datetime import datetime, timezone

logger = structlog.get_logger()


class UserService:
    def __init__(
        self, user_repository: UserRepository, password_handler: PasswordHandler
    ):
        self.user_repository = user_repository
        self.password_handler = password_handler
        self.logger = logger.bind(service="UserService")

    async def create_user(self, user_create: UserCreate) -> User:
        try:
            existing = await self.user_repository.get_by_username(user_create.username)
            if existing:
                self.logger.warning(
                    "create_user_failed_username_exists", username=user_create.username
                )
                raise ValueError("Username already exists")

            hash_password = self.password_handler.hash_password(user_create.password)

            user_insert = UserInsert(
                username=user_create.username,
                hash_password=hash_password,
            )

            result = await self.user_repository.create(user_insert)

            self.logger.info("user_registered", user_id=str(result.inserted_id))

            return User(
                id=str(result.inserted_id),
                username=user_insert.username,
                createdAt=user_insert.created_at,
                updatedAt=user_insert.updated_at,
                role=user_insert.role,
            )

        except ValueError as ve:
            self.logger.error("validation_error_create_user", error=str(ve))
            raise
        except Exception as e:
            self.logger.error("unexpected_error_create_user", error=str(e))
            raise

    async def update_user(
        self, user_id: str, update_request: UserUpdateRequest
    ) -> User:
        exists = await self.user_repository.get_by_id(user_id)

        if not exists:
            self.logger.warning("update_nonexisting_user", user_id=user_id)
            raise ValueError("Cannot update nonexisting user")

        data_dict = update_request.model_dump()
        data_dict["updated_at"] = datetime.now(timezone.utc)
        update_data = {k: v for k, v in data_dict.items() if v is not None}

        result = await self.user_repository.update(user_id, update_data)
        self.logger.info(
            "user_updated",
            user_id=user_id,
            matched_count=result.matched_count,
            modified_count=result.modified_count,
        )

        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise RuntimeError(
                f"User {user_id} not found after update — data integrity issue"
            )

        return User(
            id=user.id,
            username=user.username,
            createdAt=user.created_at,
            updatedAt=user.updated_at,
            role=user.role,
        )

    async def delete_user(self, user_id: str) -> None:
        try:
            existing_user = await self.user_repository.get_by_id(user_id)
            if not existing_user:
                self.logger.warning("delete_failed_user_not_found", user_id=user_id)
                raise ValueError("User not found")

            result = await self.user_repository.delete(user_id)
            self.logger.info(
                "user_deleted", user_id=user_id, deleted_count=result.deleted_count
            )
            if result.deleted_count == 0:
                self.logger.error("delete_user_failed_no_rows_deleted", user_id=user_id)
                raise RuntimeError("Delete operation failed")

            return
        except ValueError as ve:
            self.logger.error("validation_error_delete_user", error=str(ve))
            raise
        except Exception as e:
            self.logger.error("unexpected_error_delete_user", error=str(e))
            raise

    async def get_by_username(self, username: str) -> Optional[User]:
        try:
            user = await self.user_repository.get_by_username(username)
            if user:
                self.logger.info("user_retrieved_by_username", username=username)
                return User(
                    id=user.id,
                    username=user.username,
                    createdAt=user.created_at,
                    updatedAt=user.updated_at,
                    role=user.role,
                )
            self.logger.info("user_not_found_by_username", username=username)
            return None
        except Exception as e:
            self.logger.error("error_get_by_username", username=username, error=str(e))
            raise

    async def get_by_id(self, user_id: str) -> Optional[User]:
        try:
            user = await self.user_repository.get_by_id(user_id)
            if user:
                self.logger.info("user_retrieved_by_id", user_id=user_id)
                return User(
                    id=user.id,
                    username=user.username,
                    createdAt=user.created_at,
                    updatedAt=user.updated_at,
                    role=user.role,
                )
            self.logger.info("user_not_found_by_id", user_id=user_id)
            return None
        except Exception as e:
            self.logger.error("error_get_by_id", user_id=user_id, error=str(e))
            raise

    async def verify_credentials(
        self, username: str, password: str
    ) -> Optional[UserDB]:
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
