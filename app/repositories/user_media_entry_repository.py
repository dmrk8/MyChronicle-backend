from typing import List, Optional
from uuid import UUID
from pymongo import ReturnDocument
from bson import ObjectId
from app.models.db.db_context_model import DBOpContext
from app.models.db.user_media_entry_models import (
    UserMediaEntryDB,
    UserMediaEntryInsert,
    UserMediaEntrySyncMetadata,
    UserMediaEntryUpdate,
)
from app.repositories._base_repository import CRUDRepository
from app.repositories._repo_observability import run_db_op

from app.repositories.mixins.soft_delete_mixin import SoftDeleteMixin


class UserMediaEntryRepository(
    CRUDRepository[UserMediaEntryDB, UserMediaEntryInsert, UserMediaEntryUpdate],
    SoftDeleteMixin,
):
    db_model = UserMediaEntryDB

    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [
                ("user_id", 1),
                ("external_id", 1),
                ("external_source", 1),
                ("media_type", 1),
            ],
            unique=True,
            name="user_external_id_source_media_type_idx",
        )

    async def insert_entry(self, entry: UserMediaEntryInsert) -> UserMediaEntryDB:
        return await self._insert(
            entry,
            self._make_context(
                operation="insert_one",
                user_id=str(entry.user_id),
                media_id=str(entry.media_id),
                media_type=entry.media_type,
            ),
        )

    async def get_entry_by_id_and_user_id(
        self, entry_id: UUID, user_id: UUID
    ) -> Optional[UserMediaEntryDB]:
        return await self._find_one(
            {"_id": entry_id, "user_id": user_id},
            self._make_context(
                operation="find_one_by_id",
                entry_id=str(entry_id),
                user_id=str(user_id),
            ),
        )

    async def get_entry_by_media_id_and_user_id(
        self,
        media_id: UUID,
        user_id: UUID,
    ) -> Optional[UserMediaEntryDB]:
        return await self._find_one(
            {
                "media_id": media_id,
                "user_id": user_id,
            },
            self._make_context(
                operation="find_one_by_media_id_and_user_id",
                media_id=str(media_id),
                user_id=str(user_id),
            ),
        )

    async def update_entry(
        self,
        entry_id: UUID,
        user_id: UUID,
        update: UserMediaEntryUpdate,
    ) -> Optional[UserMediaEntryDB]:
        return await self._find_one_and_update(
            {"_id": entry_id, "user_id": user_id},
            update,
            self._make_context(
                operation="find_one_and_update",
                entry_id=str(entry_id),
                user_id=str(user_id),
            ),
        )

    async def delete_entry(self, entry_id: UUID, user_id: UUID) -> bool:
        return await self._delete_one(
            {"_id": entry_id, "user_id": user_id},
            self._make_context(
                operation="delete_one",
                entry_id=str(entry_id),
                user_id=str(user_id),
            ),
        )

    async def count_entries_by_user_id(self, user_id: UUID) -> int:
        return await self._count(
            {"user_id": user_id},
            self._make_context(operation="count_documents", user_id=str(user_id)),
        )

    async def count_entries_with_filters(self, user_id: UUID, filters: dict) -> int:
        return await self._count(
            {**filters, "user_id": user_id},
            self._make_context(operation="count_documents", user_id=str(user_id)),
        )

    async def get_entries_with_filters(
        self,
        user_id: UUID,
        filters: dict,
        page: int,
        per_page: int,
        sort_by: str,
        sort_order: int,
    ) -> List[UserMediaEntryDB]:
        return await self._find_many(
            {**filters, "user_id": user_id},
            self._make_context(operation="find_many", user_id=str(user_id)),
            sort_by=sort_by,
            sort_order=sort_order,
            skip=(page - 1) * per_page,
            limit=per_page,
        )

    async def delete_by_user_id(self, user_id: UUID) -> bool:
        return await self._delete_many(
            {"user_id": user_id},
            self._make_context(operation="delete_many", user_id=str(user_id)),
        )

    async def sync_entry_metadata(
        self, entry_id: UUID, user_id: UUID, metadata: UserMediaEntrySyncMetadata
    ) -> Optional[UserMediaEntryDB]:
        """Sync metadata from external API"""
        update_dict = metadata.model_dump(exclude_unset=True)
        context = DBOpContext(
            entry_id=str(entry_id),
            user_id=str(user_id),
            operation="sync_metadata",
            collection=self.collection.name,
        )

        async def _op():
            return await self.collection.find_one_and_update(
                {"_id": entry_id, "user_id": user_id},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_sync_metadata",
            error_event="mongo_user_media_entry_sync_metadata_error",
            context=context,
        )

        return UserMediaEntryDB.model_validate(doc) if doc else None

    async def soft_delete_by_id(self, entry_id: UUID, user_id: UUID) -> bool:
        return await self._soft_delete(
            {"_id": entry_id, "user_id": user_id},
            self._make_context(
                operation="soft_delete_one", entry_id=str(entry_id), user_id=str(user_id)
            ),
        )
    
    async def soft_delete_many_by_user_id(self, user_id: UUID) -> bool:
        return await self._soft_delete_many(
            {"user_id": user_id},
            self._make_context(operation="soft_delete_many", user_id=str(user_id)),
        )
