from pymongo.errors import DuplicateKeyError
import structlog
from typing import Optional

from app.auth import password_handler
from app.core.exceptions import AuthenticationError, ConflictException
from app.models.user_models import User, UserInsert, UserUpdate
from app.repositories.user_repository import UserRepository

logger = structlog.get_logger()


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_handler: password_handler.PasswordHandler,
    ):
        self.user_repository = user_repository
        self.password_handler = password_handler
        self.logger = logger.bind(service="UserService")

    async def create_user(self, username: str, password: str) -> User:
        try:
            hash_password = self.password_handler.hash_password(password)
            user_insert = UserInsert(username=username, hash_password=hash_password)
            res = await self.user_repository.create(user_insert)
            return User.from_db(res)
        except DuplicateKeyError:
            raise ConflictException("Username already exists")

    async def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        res = await self.user_repository.update(user_id, user_update)
        if res is None:
            raise RuntimeError("User missing after update - data integrity issue")

        return User.from_db(res)

    async def update_username(self, user_id: str, username: str) -> None:
        update_data = UserUpdate(username=username)  # type: ignore
        res = await self.user_repository.update(user_id, update_data)
        if res is None:
            raise RuntimeError("User missing after update - data integrity issue")

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise RuntimeError("User missing for password change")

        if not self.password_handler.verify_password(
            current_password, user.hash_password
        ):
            raise AuthenticationError("Current password is incorrect")

        new_hash = self.password_handler.hash_password(new_password)
        user_update = UserUpdate(hash_password=new_hash)  # type: ignore

        res = await self.user_repository.update(user_id, user_update)
        if res is None:
            raise RuntimeError("Password update failed")

    async def delete_user(self, user_id: str) -> None:
        result = await self.user_repository.delete(user_id)
        if result.deleted_count == 0:
            raise RuntimeError(f"Delete operation had no effect for user {user_id}")
        self.logger.info("user_deleted", user_id=user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        user = await self.user_repository.get_by_username(username)
        if not user:
            self.logger.info("user_not_found", lookup="username", username=username)
            return None

        self.logger.info("user_retrieved", lookup="username", username=username)
        return User.from_db(user)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            self.logger.info("user_not_found", lookup="id", user_id=user_id)
            return None

        self.logger.info("user_retrieved", lookup="id", user_id=user_id)
        return User.from_db(user)

    async def verify_credentials(self, username: str, password: str) -> Optional[User]:
        """
        Verify username and password combination.
        Returns user if credentials are valid, None otherwise.
        Used by AuthService for login.
        """
        try:
            user = await self.user_repository.get_by_username(username)

            if not user:
                self.logger.info("authentication_failed", reason="user_not_found")
                raise AuthenticationError("Invalid username or password")

            if not self.password_handler.verify_password(password, user.hash_password):
                self.logger.warning("authentication_failed", reason="invalid_password")
                raise AuthenticationError("Invalid username or password")

            self.logger.info("credentials_verified", user_id=user.id)
            return User.from_db(user)
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error("error_verifying_credentials", error=str(e))
            raise RuntimeError("Credential verification failed")
