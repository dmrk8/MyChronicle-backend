from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import DeleteResult, InsertOneResult
from bson import ObjectId
from app.models.user_media_entry_models import (
    UserMediaEntryDB,
    UserMediaEntryInsert,
    UserMediaEntrySyncMetadata,
    UserMediaEntryUpdate,
)
from app.repositories._repo_observability import run_db_op
import structlog

logger = structlog.get_logger()


class UserMediaEntryRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = self.db[collection_name]
        self.logger = logger.bind(
            repository="UserMediaEntryRepository", collection=collection_name
        )

    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [
                ("user_id", 1),
                ("external_id", 1),
                ("external_source", 1),
            ],
            unique=True,
            name="user_external_unique_idx",
        )

    async def create_entry(self, entry: UserMediaEntryInsert) -> UserMediaEntryDB:
        data = entry.model_dump()

        async def _op() -> InsertOneResult:
            return await self.collection.insert_one(data)

        try:
            result = await run_db_op(
                self.logger,
                _op,
                success_event="mongo_user_media_entry_insert_one",
                error_event="mongo_user_media_entry_insert_one_error",
                context={"user_id": entry.user_id, "external_id": entry.external_id},
            )
            return UserMediaEntryDB(**{**data, "_id": result.inserted_id})
        except DuplicateKeyError:
            self.logger.warning(
                "mongo_user_media_entry_insert_duplicate",
                user_id=entry.user_id,
                external_id=entry.external_id,
            )
            raise

    async def get_entry_by_id(
        self, entry_id: str, user_id: str
    ) -> Optional[UserMediaEntryDB]:
        async def _op():
            return await self.collection.find_one(
                {"_id": ObjectId(entry_id), "user_id": user_id}
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_find_one_by_id_query",
            error_event="mongo_user_media_entry_find_one_by_id_error",
            context={"user_id": user_id, "entry_id": entry_id},
        )

        if doc:
            self.logger.info(
                "mongo_user_media_entry_find_one_by_id_found",
                entry_id=entry_id,
                user_id=user_id,
            )
            return UserMediaEntryDB.model_validate(doc)

        self.logger.info(
            "mongo_user_media_entry_find_one_by_id_not_found",
            entry_id=entry_id,
            user_id=user_id,
        )
        return None

    async def get_entry_by_external_id_and_external_source_and_user_id(
        self, external_id: int, external_source: str, user_id: str
    ) -> Optional[UserMediaEntryDB]:
        async def _op():
            return await self.collection.find_one(
                {
                    "external_id": external_id,
                    "external_source": external_source,
                    "user_id": user_id,
                }
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_find_one_by_external_id_and_user_id_query",
            error_event="mongo_user_media_entry_find_one_by_external_id_and_user_id_error",
            context={
                "external_id": external_id,
                "external_source": external_source,
                "user_id": user_id,
            },
        )

        if doc:
            self.logger.info(
                "mongo_user_media_entry_find_one_by_media_id_and_user_id_found",
                external_id=external_id,
                user_id=user_id,
            )
            return UserMediaEntryDB.model_validate(doc)

        self.logger.info(
            "mongo_user_media_entry_find_one_by_external_id_and_user_id_not_found",
            external_id=external_id,
            user_id=user_id,
        )
        return None

    async def update_entry(
        self, entry_id: str, user_id: str, update: UserMediaEntryUpdate
    ) -> Optional[UserMediaEntryDB]:
        update_dict = update.to_update_dict()

        async def _op():
            return await self.collection.find_one_and_update(
                {"_id": ObjectId(entry_id), "user_id": user_id},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_update_query",
            error_event="mongo_user_media_entry_update_one_error",
            context={"entry_id": entry_id, "user_id": user_id},
        )

        if doc:
            self.logger.info(
                "mongo_user_media_entry_update_success",
                entry_id=entry_id,
                user_id=user_id,
            )
            return UserMediaEntryDB.model_validate(doc)

        self.logger.warning(
            "mongo_user_media_entry_update_not_found_or_forbidden",
            entry_id=entry_id,
            user_id=user_id,
        )
        return None

    async def sync_entry_metadata(
        self, entry_id: str, user_id: str, metadata: UserMediaEntrySyncMetadata
    ) -> Optional[UserMediaEntryDB]:
        """Sync metadata from external API"""
        update_dict = metadata.to_update_dict()

        async def _op():
            return await self.collection.find_one_and_update(
                {"_id": ObjectId(entry_id), "user_id": user_id},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_sync_metadata",
            error_event="mongo_user_media_entry_sync_metadata_error",
            context={"entry_id": entry_id, "user_id": user_id},
        )

        if doc:
            return UserMediaEntryDB.model_validate(doc)
        return None

    async def delete_entry(self, entry_id: str, user_id: str) -> DeleteResult:
        async def _op() -> DeleteResult:
            return await self.collection.delete_one(
                {"_id": ObjectId(entry_id), "user_id": user_id}
            )

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_delete_query",
            error_event="mongo_user_media_entry_delete_one_error",
            context={"entry_id": entry_id, "user_id": user_id},
        )

        if result.deleted_count == 0:
            self.logger.warning(
                "mongo_user_media_entry_delete_not_found_or_forbidden",
                entry_id=entry_id,
                user_id=user_id,
            )
        else:
            self.logger.info(
                "mongo_user_media_entry_delete_success",
                entry_id=entry_id,
                user_id=user_id,
                deleted_count=result.deleted_count,
            )
        return result

    async def count_entries_by_user_id(self, user_id: str) -> int:
        async def _op() -> int:
            return await self.collection.count_documents({"user_id": user_id})

        count = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_count_by_user_id",
            error_event="mongo_user_media_entry_count_by_user_id_error",
            context={"user_id": user_id},
        )

        self.logger.info(
            "mongo_user_media_entry_count_result",
            user_id=user_id,
            count=count,
        )
        return count

    async def count_entries(self, user_id: str, filters: dict) -> int:
        query = {**filters, "user_id": user_id}

        async def _op() -> int:
            return await self.collection.count_documents(query)

        count = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_count_entries",
            error_event="mongo_user_media_entry_count_entries_error",
            context={"user_id": user_id},
        )

        self.logger.info(
            "mongo_user_media_entry_count_entries_result",
            user_id=user_id,
            count=count,
        )
        return count

    async def get_entries(
        self,
        user_id: str,
        filters: dict,
        page: int,
        per_page: int,
        sort_by: str,
        sort_order: int,
    ) -> List[UserMediaEntryDB]:
        skip = (page - 1) * per_page

        query = {**filters, "user_id": user_id}

        async def _op():
            cursor = (
                self.collection.find(query)
                .sort(sort_by, sort_order)
                .skip(skip)
                .limit(per_page)
            )
            return [UserMediaEntryDB(**doc) async for doc in cursor]

        results = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_get_entries",
            error_event="mongo_user_media_entry_get_entries_error",
            context={
                "user_id": user_id,
                "page": page,
                "per_page": per_page,
                "sort_by": sort_by,
                "sort_order": sort_order,
            },
        )

        self.logger.info(
            "mongo_user_media_entry_get_entries_result",
            count=len(results),
        )
        return results
    
    async def delete_by_user_id(self, user_id: str) -> DeleteResult:
        async def _op() -> DeleteResult:
            return await self.collection.delete_many({"user_id": user_id})

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_media_entry_delete_by_user_id",
            error_event="mongo_user_media_entry_delete_by_user_id_error",
            context={"user_id": user_id},
        )

        self.logger.info(
            "mongo_user_media_entry_delete_by_user_id_result",
            user_id=user_id,
            deleted_count=result.deleted_count,
        )
        return result
