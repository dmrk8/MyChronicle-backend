from typing import Optional
from uuid import UUID

from app.models.db.user_models import UserDB, UserInsert, UserUpdate
from app.repositories._base_repository import CRUDRepository
from app.repositories.mixins.soft_delete_mixin import SoftDeleteMixin


class UserRepository(CRUDRepository[UserDB, UserInsert, UserUpdate], SoftDeleteMixin):
    db_model = UserDB

    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [
                ("username", 1),
            ],
            unique=True,
            name="username_unique_idx",
        )

    async def insert_user(self, user: UserInsert) -> UserDB:
        return await self._insert(
            user, self._make_context(operation="insert_one", username=user.username)
        )

    async def update(self, id: UUID, update_data: UserUpdate) -> Optional[UserDB]:
        return await self._find_one_and_update(
            {"_id": id, "is_deleted": False},
            update_data,
            self._make_context(operation="update_one", user_id=str(id)),
        )

    async def delete(self, user_id: UUID) -> bool:
        return await self._delete_one(
            {"_id": user_id, "is_deleted": False},
            self._make_context(operation="delete_one", user_id=str(user_id)),
        )

    async def get_by_id(self, id: UUID) -> Optional[UserDB]:
        return await self._find_one(
            {"_id": id, "is_deleted": False},
            self._make_context(operation="find_one_by_id", user_id=str(id)),
        )

    async def get_by_username(self, username: str) -> Optional[UserDB]:
        return await self._find_one(
            {"username": username, "is_deleted": False},
            self._make_context(operation="find_one_by_username", username=username),
        )

    async def soft_delete_by_id(self, user_id: UUID) -> bool:
        return await self._soft_delete(
            {"_id": user_id, "is_deleted": False},
            self._make_context(operation="soft_delete_one", user_id=str(user_id)),
        )
