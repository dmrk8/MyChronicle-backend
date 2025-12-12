import logging
from typing import List, Optional
from app.repositories.user_repository import UserRepository
from app.models.user_models import UserDB, UserUpdate, UserResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_data: UserDB) -> UserResponse:
        try:
            user = UserDB(
                username=user_data.username,
                hash_password=hashed_password,  # type: ignore
                role=user_data.role,
            )

            result = self.user_repository.create(user_data)
            logger.info(f"User created with id {result.inserted_id}")

            return UserResponse(
                message="User created successfully",
                data=user_data,
                user_id=str(result.inserted_id),  # type: ignore
                acknowledged=result.acknowledged,
            )

        except ValueError as ve:
            logger.error(f"Validation error in create_user: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_user: {e}")
            raise

    def update_user(self, user_id: str, user_update: UserUpdate) -> UserResponse:
        pass

    def delete_user(self, user_id: str) -> UserResponse:
        try:
            existing_user = self.user_repository.get_by_id(user_id)
            if not existing_user:
                logger.warning(f"Delete failed: user {user_id} not found")
                raise ValueError("User not found")

            result = self.user_repository.delete(user_id)
            logger.info(f"User {user_id} deleted, deleted count: {result.deleted_count}")

            return UserResponse(
                message="User deleted successfully",
                user_id=user_id,  # type: ignore
                acknowledged=result.acknowledged,
            )

        except ValueError as ve:
            logger.error(f"Validation error in delete_user: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in delete_user: {e}")
            raise

    def get_by_username(self, username: str) -> Optional[UserDB]:
        try:
            user = self.user_repository.get_by_username(username)
            if user:
                logger.info(f"Retrieved user {username}")
                return user
            logger.info(f"No user found with username {username}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {e}")
            raise

    def get_by_id(self, user_id: str) -> Optional[UserDB]:
        try:
            user = self.user_repository.get_by_id(user_id)
            if user:
                logger.info(f"Retrieved user by id {user_id}")
                return user
            logger.info(f"No user found with id {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by id {user_id}: {e}")
            raise
