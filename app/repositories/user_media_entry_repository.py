from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from pymongo.errors import PyMongoError
from bson import ObjectId
from app.models.user_media_entry_models import UserMediaEntryDB
import structlog
import time

logger = structlog.get_logger()


class UserMediaEntryRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = self.db[collection_name]
        self.logger = logger.bind(repository="UserMediaEntryRepository", collection=collection_name)

    def map_to_model(self, mongo_doc: dict) -> UserMediaEntryDB:
        mongo_doc["id"] = str(mongo_doc["_id"])
        mongo_doc.pop("_id", None)
        return UserMediaEntryDB(**mongo_doc)

    async def create_entry(self, entry_data: UserMediaEntryDB) -> InsertOneResult:
        start = time.perf_counter()
        try:
            data = entry_data.model_dump()
            data.pop("id", None)
            result = await self.collection.insert_one(data)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_media_entry_insert_one",
                entry_id=str(result.inserted_id),
                elapsed_ms=elapsed_ms,
            )
            return result
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_media_entry_insert_one_error", error=str(e), elapsed_ms=elapsed_ms
            )
            raise

    async def get_entry_by_id(self, entry_id: str) -> UserMediaEntryDB:
        start = time.perf_counter()
        try:
            data = await self.collection.find_one({"_id": ObjectId(entry_id)})
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            if data:
                self.logger.info(
                    "mongo_user_media_entry_find_one_by_id_found",
                    entry_id=entry_id,
                    elapsed_ms=elapsed_ms,
                )
                return self.map_to_model(data)
            self.logger.info(
                "mongo_user_media_entry_find_one_by_id_not_found",
                entry_id=entry_id,
                elapsed_ms=elapsed_ms,
            )
            raise
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_media_entry_find_one_by_id_error",
                error=str(e),
                entry_id=entry_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def update_entry(self, entry_id: str, update_data: dict) -> UpdateResult:
        start = time.perf_counter()
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(entry_id)}, {"$set": update_data}
            )
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_media_entry_update_one",
                entry_id=entry_id,
                matched_count=result.matched_count,
                modified_count=result.modified_count,
                elapsed_ms=elapsed_ms,
            )
            return result
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_media_entry_update_one_error", error=str(e), elapsed_ms=elapsed_ms
            )
            raise

    async def delete_entry(self, entry_id: str) -> DeleteResult:
        start = time.perf_counter()
        try:
            result = await self.collection.delete_one({"_id": ObjectId(entry_id)})
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_media_entry_delete_one",
                entry_id=entry_id,
                deleted_count=result.deleted_count,
                elapsed_ms=elapsed_ms,
            )
            return result
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_media_entry_delete_one_error",
                error=str(e),
                entry_id=entry_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def get_entries_by_user_id(self, user_id: str) -> List[UserMediaEntryDB]:
        start = time.perf_counter()
        try:
            cursor = self.collection.find({"user_id": user_id})
            results = [self.map_to_model(doc) async for doc in cursor]
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_media_entry_find_by_user_id",
                user_id=user_id,
                count=len(results),
                elapsed_ms=elapsed_ms,
            )
            return results
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_media_entry_find_by_user_id_error",
                error=str(e),
                user_id=user_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def count_entries_by_user_id(self, user_id: str) -> int:
        start = time.perf_counter()
        try:
            count = await self.collection.count_documents({"user_id": user_id})
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_media_entry_count_by_user_id",
                user_id=user_id,
                count=count,
                elapsed_ms=elapsed_ms,
            )
            return count
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_media_entry_count_by_user_id_error",
                error=str(e),
                user_id=user_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def get_entry_by_external_id_and_user_id(
        self, external_id: int, user_id: str
    ) -> UserMediaEntryDB:
        start = time.perf_counter()
        try:
            data = await self.collection.find_one({"external_id": external_id, "user_id": user_id})
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            if data:
                self.logger.info(
                    "mongo_user_media_entry_find_one_by_media_id_and_user_id_found",
                    external_id=external_id,
                    user_id=user_id,
                    elapsed_ms=elapsed_ms,
                )
                return self.map_to_model(data)
            self.logger.info(
                "mongo_user_media_entry_find_one_by_external_id_and_user_id_not_found",
                external_id=external_id,
                user_id=user_id,
                elapsed_ms=elapsed_ms,
            )
            raise
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_media_entry_find_one_by_external_id_and_user_id_error",
                error=str(e),
                external_id=external_id,
                user_id=user_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def get_entries(
        self,
        filters: dict,
        page: int,
        per_page: int,
        sort_by: str,
        sort_order: int,
    ) -> List[UserMediaEntryDB]:
        """
        Get user media entries with pagination, sorting, and filters.

        :param filters: MongoDB filter dict
        :param page: Page number (1-based)
        :param per_page: Number of items per page
        :param sort_by: Field to sort by
        :param sort_order: 1 for ascending, -1 for descending
        :return: List of UserMediaEntryDB
        """
        start = time.perf_counter()
        try:
            filters = filters or {}
            skip = (page - 1) * per_page
            cursor = (
                self.collection.find(filters).sort(sort_by, sort_order).skip(skip).limit(per_page)
            )
            results = [self.map_to_model(doc) async for doc in cursor]
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_media_entry_get_entries",
                count=len(results),
                elapsed_ms=elapsed_ms,
            )
            return results
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_media_entry_get_entries_error",
                error=str(e),
                elapsed_ms=elapsed_ms,
            )
            raise

    async def is_exists(self, entry_id: str) -> bool:
        return await self.collection.count_documents({"_id": ObjectId(entry_id)}, limit=1) > 0
