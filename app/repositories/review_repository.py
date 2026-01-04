from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from pymongo.errors import PyMongoError
from bson import ObjectId
from app.models.review_models import ReviewDB
import structlog
import time

logger = structlog.get_logger()


class ReviewRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = self.db[collection_name]
        self.logger = logger.bind(repository="ReviewRepository", collection=collection_name)

    def map_to_model(self, mongo_doc: dict) -> ReviewDB:
        mongo_doc["id"] = str(mongo_doc["_id"])
        mongo_doc.pop("_id", None)
        return ReviewDB(**mongo_doc)

    async def is_exists(self, review_id: str) -> bool:
        start = time.perf_counter()
        try:
            exists = (
                await self.collection.count_documents({"_id": ObjectId(review_id)}, limit=1) > 0
            )
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_review_exists",
                review_id=review_id,
                exists=exists,
                elapsed_ms=elapsed_ms,
            )
            return exists
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_exists_error",
                error=str(e),
                review_id=review_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def create_review(self, review_data: ReviewDB) -> InsertOneResult:
        start = time.perf_counter()
        try:
            data = review_data.model_dump()
            data.pop("id", None)
            result = await self.collection.insert_one(data)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_review_insert_one", review_id=str(result.inserted_id), elapsed_ms=elapsed_ms
            )
            return result
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_insert_one_error", error=str(e), elapsed_ms=elapsed_ms
            )
            raise

    async def delete_review(self, review_id: str) -> DeleteResult:
        start = time.perf_counter()
        try:
            result = await self.collection.delete_one({"_id": ObjectId(review_id)})
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_review_delete_one",
                review_id=review_id,
                deleted_count=result.deleted_count,
                elapsed_ms=elapsed_ms,
            )
            return result
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_delete_one_error",
                error=str(e),
                review_id=review_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def update_review(self, review_id: str, update_data: dict) -> UpdateResult:
        start = time.perf_counter()
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(review_id)}, {"$set": update_data}
            )
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_review_update_one",
                review_id=review_id,
                matched_count=result.matched_count,
                modified_count=result.modified_count,
                elapsed_ms=elapsed_ms,
            )
            return result
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_update_one_error", error=str(e), elapsed_ms=elapsed_ms
            )
            raise

    async def get_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str
    ) -> Optional[List[ReviewDB]]:
        start = time.perf_counter()
        try:
            cursor = self.collection.find({"user_media_entry_id": user_media_entry_id})
            results = [self.map_to_model(doc) async for doc in cursor]
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_review_find_by_user_media_entry_id",
                user_media_entry_id=user_media_entry_id,
                count=len(results),
                elapsed_ms=elapsed_ms,
            )
            return results
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_find_by_user_media_entry_id_error",
                error=str(e),
                user_media_entry_id=user_media_entry_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def get_review_by_id(self, review_id: str) -> Optional[ReviewDB]:
        start = time.perf_counter()
        try:
            data = await self.collection.find_one({"_id": ObjectId(review_id)})
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            if data:
                self.logger.info(
                    "mongo_review_find_one_by_id_found", review_id=review_id, elapsed_ms=elapsed_ms
                )
                return self.map_to_model(data)
            self.logger.info(
                "mongo_review_find_one_by_id_not_found", review_id=review_id, elapsed_ms=elapsed_ms
            )
            return None
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_find_one_by_id_error",
                error=str(e),
                review_id=review_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def count_reviews_by_user_media_entry_id(self, user_media_entry_id: str) -> int:
        start = time.perf_counter()
        try:
            query = {"user_media_entry_id": user_media_entry_id}
            count = await self.collection.count_documents(query)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_review_count_by_user_media_entry_id",
                user_media_entry_id=user_media_entry_id,
                count=count,
                elapsed_ms=elapsed_ms,
            )
            return count
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_count_by_user_media_entry_id_error",
                error=str(e),
                user_media_entry_id=user_media_entry_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def delete_reviews_by_user_media_entry_id(self, user_media_entry_id: str) -> DeleteResult:
        start = time.perf_counter()
        try:
            result = await self.collection.delete_many({"user_media_entry_id": user_media_entry_id})
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_review_delete_many_by_user_media_entry_id",
                user_media_entry_id=user_media_entry_id,
                deleted_count=result.deleted_count,
                elapsed_ms=elapsed_ms,
            )
            return result
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_delete_many_by_user_media_entry_id_error",
                error=str(e),
                user_media_entry_id=user_media_entry_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def get_reviews_by_user_id_and_media_id(
        self, user_id: str, media_id: str
    ) -> Optional[List[ReviewDB]]:
        start = time.perf_counter()
        try:
            cursor = self.collection.find({"user_id": user_id, "media_id": media_id})
            results = [self.map_to_model(doc) async for doc in cursor]
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_review_find_by_user_id_and_media_id",
                user_id=user_id,
                media_id=media_id,
                count=len(results),
                elapsed_ms=elapsed_ms,
            )
            return results
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_review_find_by_user_id_and_media_id_error",
                error=str(e),
                user_id=user_id,
                media_id=media_id,
                elapsed_ms=elapsed_ms,
            )
            raise
