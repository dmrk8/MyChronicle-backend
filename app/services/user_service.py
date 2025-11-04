from typing import List, Optional
from app.repositories.user_repository import UserRepository
from app.models.user_models import UserLogin, UserData
from app.auth.jwt_handler import hash_password


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def create_user(self, user_login : UserLogin) -> str:
        try:
            if self.user_repository.is_username_exists(user_login.username):
                raise ValueError("username is already exists")

            hashed_password = hash_password(user_login.password)

            user_data = UserData(
                username=user_login.username,
                hash_password=hashed_password,
            ) 

            result = self.user_repository.create(user_data)
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
        
    def get_by_username(self, username: str) -> Optional[UserData]:
        try:
            user = self.user_repository.get_by_username(username)
            if user:
                return user
            return None
        except Exception as e:
            print(f"Error retrieving user by username {username}: {e}")
            raise