from pymongo.errors import DuplicateKeyError
import structlog
from typing import Optional

from app.auth import password_handler
from app.core.event_bus import EventBus
from app.core.exceptions import (
    ConflictException,
    InternalServerErrorException,
    NotFoundException,
    UnauthorizedException,
)
from app.models.db.user_models import (
    UserDB,
    UserInsert,
    UserUpdate,
    PasswordUpdateRequest,
    UsernameUpdateRequest,
)
from app.repositories.user_repository import UserRepository

logger = structlog.get_logger()


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_handler: password_handler.PasswordHandler,
        event_bus: EventBus | None = None,
    ):
        self.user_repository = user_repository
        self.password_handler = password_handler
        self.event_bus = event_bus
        self.logger = logger.bind(service="UserService")

    async def create_user(self, username: str, password: str) -> UserDB:
        hash_password = self.password_handler.hash_password(password)
        user_insert = UserInsert(username=username, hash_password=hash_password)
        try:
            res = await self.user_repository.insert_user(user_insert)
        except DuplicateKeyError:
            raise ConflictException("Username already exists")
        if res is None:
            self.logger.error("user_creation_failed", username=username)
            raise InternalServerErrorException("User creation failed.")

        self.logger.info("user_created", user_id=res.id, username=username)
        return res

    async def update_username(
        self, user_id: str, update: UsernameUpdateRequest
    ) -> UserDB:
        update_data = UserUpdate(username=update.username)  # type: ignore
        try:
            res = await self.user_repository.update(user_id, update_data)
        except DuplicateKeyError:
            raise ConflictException("Username already exists")
        if res is None:
            raise NotFoundException("User not found")
        self.logger.info("username_updated", user_id=user_id, username=update.username)
        return res

    async def change_password(
        self, user_id: str, update_password: PasswordUpdateRequest
    ) -> UserDB:
        """User is already authenticated in router. No need for additional authentication."""

        new_hash = self.password_handler.hash_password(update_password.new_password)
        user_update = UserUpdate(hash_password=new_hash)  # type: ignore

        res = await self.user_repository.update(user_id, user_update)
        if res is None:
            raise InternalServerErrorException("Password update failed.")
        self.logger.info("password_updated", user_id=user_id)
        return res

    async def delete_user(self, user_id: str) -> None:
        deleted = await self.user_repository.soft_delete_by_id(user_id)
        if not deleted:
            raise NotFoundException("User not found")
        if self.event_bus:
            await self.event_bus.publish("user.soft_deleted", user_id=user_id)
        self.logger.info("user_soft_deleted", user_id=user_id)

    async def get_by_id(self, user_id: str) -> Optional[UserDB]:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def verify_credentials(
        self, username: str, password: str
    ) -> Optional[UserDB]:
        """
        Verify username and password combination.
        Returns user if credentials are valid, None otherwise.
        Used by AuthService for login.
        """
        user = await self.user_repository.get_by_username(username)

        if not user or not self.password_handler.verify_password(
            password, user.hash_password
        ):
            raise UnauthorizedException("Invalid username or password")

        return user
