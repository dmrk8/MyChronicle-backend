import logging
from datetime import datetime
from typing import List, Optional
from app.repositories.user_repository import UserRepository
from app.models.user_models import UserDB, UserUpdateRequest, UserResponse, UserCreate
from app.auth.password_handler import PasswordHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class UserService:
    def __init__(self, user_repository: UserRepository, password_handler: PasswordHandler):
        self.user_repository = user_repository
        self.password_handler = password_handler

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        try:
            existing = await self.user_repository.get_by_username(user_create.username)
            if existing:
                raise ValueError("Username already exists")

            hash_password = self.password_handler.hash_password(user_create.password)

            user_db = UserDB(username=user_create.username, hashPassword=hash_password)
            result = await self.user_repository.create(user_db)
            
            logger.info(f"User created with id {result.inserted_id}")

            return UserResponse(
                message="User created successfully",
                data=user_db,
                user_id=str(result.inserted_id),  # type: ignore
                acknowledged=result.acknowledged,
            )

        except ValueError as ve:
            logger.error(f"Validation error in create_user: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_user: {e}")
            raise

    async def update_user(self, user_id: str, update_request: UserUpdateRequest) -> UserResponse:
        exists = await self.user_repository.get_by_id(user_id)
        
        if not exists:
            raise ValueError("Cannot update nonexisting user")
        
        data_dict = update_request.model_dump()
        
        update_data = {k: v for k, v in data_dict.items() if v is not None}

        result = await self.user_repository.update(user_id, update_data)
        
        return UserResponse(
            message="User updated successfully",  
            user_id=user_id,   # type: ignore
            acknowledged=result.acknowledged,
            matched_count=result.matched_count, # type: ignore
            modified_count=result.modified_count # type: ignore
            )


    async def delete_user(self, user_id: str) -> UserResponse:
        try:
            existing_user = self.user_repository.get_by_id(user_id)
            if not existing_user:
                logger.warning(f"Delete failed: user {user_id} not found")
                raise ValueError("User not found")

            result = await self.user_repository.delete(user_id)
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

    async def get_by_username(self, username: str) -> Optional[UserDB]:
        try:
            user = await self.user_repository.get_by_username(username)
            if user:
                logger.info(f"Retrieved user {username}")
                return user
            logger.info(f"No user found with username {username}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {e}")
            raise

    async def get_by_id(self, user_id: str) -> Optional[UserDB]:
        try:
            user = await self.user_repository.get_by_id(user_id)
            if user:
                logger.info(f"Retrieved user by id {user_id}")
                return user
            logger.info(f"No user found with id {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by id {user_id}: {e}")
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
                logger.info(f"Login attempt for non-existent user: {username}")
                return None
            
            if not self.password_handler.verify_password(password, user.hash_password):
                logger.warning(f"Invalid password attempt for user: {username}")
                return None
            
            logger.info(f"Credentials verified successfully for user: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error verifying credentials for {username}: {e}")
            raise
