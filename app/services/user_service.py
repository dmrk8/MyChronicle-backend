from pymongo.errors import DuplicateKeyError
import structlog
from typing import Optional

from app.auth import password_handler
from app.core.event_bus import EventBus
from app.core.exceptions import (
    AuthenticationError,
    ConflictException,
    InternalServerErrorException,
    NotFoundException,
)
from app.models.db.user_models import (
    UpdatePasswordRequest,
    UpdateUsernameRequest,
    User,
    UserInsert,
    UserUpdate,
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

    async def create_user(self, username: str, password: str) -> User:
        hash_password = self.password_handler.hash_password(password)
        user_insert = UserInsert(username=username, hash_password=hash_password)
        try:
            res = await self.user_repository.insert_user(user_insert)
        except DuplicateKeyError:
            raise ConflictException("Username already exists")
        if res is None:
            raise InternalServerErrorException(
                "User creation failed. Data integrity issue."
            )
        self.logger.info("user_created", user_id=res.id, username=username)
        return User.from_db(res)

    async def update_username(
        self, user_id: str, update_username: UpdateUsernameRequest
    ) -> User:
        update_data = UserUpdate(username=update_username.username)  # type: ignore
        try:
            res = await self.user_repository.update(user_id, update_data)
        except DuplicateKeyError:
            raise ConflictException("Username already exists")

        if res is None:
            raise NotFoundException("User not found")
        self.logger.info(
            "username_updated", user_id=user_id, username=update_username.username
        )
        return User.from_db(res)

    async def change_password(
        self, user_id: str, update_password: UpdatePasswordRequest
    ) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")

        if not self.password_handler.verify_password(
            update_password.current_password, user.hash_password
        ):
            raise AuthenticationError("Invalid Credentials")

        new_hash = self.password_handler.hash_password(update_password.new_password)
        user_update = UserUpdate(hash_password=new_hash)  # type: ignore

        res = await self.user_repository.update(user_id, user_update)
        if res is None:
            raise InternalServerErrorException(
                "User does not exists after password update. Data integrity issue."
            )
        self.logger.info("password_updated", user_id=user_id)
        return User.from_db(res)

    async def delete_user(self, user_id: str) -> None:
        deleted = await self.user_repository.delete(user_id)
        if not deleted:
            raise NotFoundException("User not found")

        if self.event_bus:
            await self.event_bus.publish("user.deleted", user_id=user_id)
        self.logger.info("user_deleted", user_id=user_id)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        self.logger.info("user_found", user_id=user_id)
        return User.from_db(user)

    async def verify_credentials(self, username: str, password: str) -> Optional[User]:
        """
        Verify username and password combination.
        Returns user if credentials are valid, None otherwise.
        Used by AuthService for login.
        """
        user = await self.user_repository.get_by_username(username)

        if not user:
            raise AuthenticationError("Invalid username or password")

        if not self.password_handler.verify_password(password, user.hash_password):
            raise AuthenticationError("Invalid username or password")

        self.logger.info("credentials_verified", user_id=user.id)
        return User.from_db(user)
