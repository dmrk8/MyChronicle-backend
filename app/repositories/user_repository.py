import structlog
import time
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from pymongo.errors import PyMongoError
from app.models.user_models import UserDB, UserInsert

logger = structlog.get_logger()


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = db[collection_name]
        self.logger = logger.bind(
            repository="UserRepository", collection=collection_name
        )

    def map_to_model(self, mongo_doc: dict) -> UserDB:
        mongo_doc["id"] = str(mongo_doc["_id"])
        mongo_doc.pop("_id", None)
        return UserDB(**mongo_doc)

    async def create(self, user: UserInsert) -> InsertOneResult:
        start = time.perf_counter()
        try:
            data = user.model_dump()

            result = await self.collection.insert_one(data)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_insert_one",
                user_id=str(result.inserted_id),
                elapsed_ms=elapsed_ms,
            )
            return result

        except PyMongoError:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception("mongo_user_insert_one_error", elapsed_ms=elapsed_ms)
            raise

    async def update(self, id: str, update_data: dict) -> UpdateResult:
        start = time.perf_counter()
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(id)}, {"$set": update_data}
            )
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_update_one",
                user_id=id,
                matched_count=result.matched_count,
                modified_count=result.modified_count,
                elapsed_ms=elapsed_ms,
            )
            return result
        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_update_one_error",
                error=str(e),
                user_id=id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def delete(self, user_id: str) -> DeleteResult:
        start = time.perf_counter()
        try:
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_delete_one",
                user_id=user_id,
                deleted_count=result.deleted_count,
                elapsed_ms=elapsed_ms,
            )
            return result

        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_delete_one_error",
                error=str(e),
                user_id=user_id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def get_by_id(self, id: str) -> Optional[UserDB]:
        start = time.perf_counter()
        try:
            user_doc = await self.collection.find_one({"_id": ObjectId(id)})

            elapsed_ms = int((time.perf_counter() - start) * 1000)
            if user_doc:
                self.logger.info(
                    "mongo_user_find_one_by_id_found", user_id=id, elapsed_ms=elapsed_ms
                )
                return self.map_to_model(user_doc)
            self.logger.info(
                "mongo_user_find_one_by_id_not_found", user_id=id, elapsed_ms=elapsed_ms
            )
            return None

        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_find_one_by_id_error",
                error=str(e),
                user_id=id,
                elapsed_ms=elapsed_ms,
            )
            raise

    async def is_username_exists(self, username: str) -> bool:
        start = time.perf_counter()
        try:
            user_doc = await self.collection.find_one({"username": username})
            exists = user_doc is not None
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.info(
                "mongo_user_find_one_by_username_exists",
                exists=exists,
                elapsed_ms=elapsed_ms,
            )
            return exists

        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_find_one_by_username_error",
                error=str(e),
                elapsed_ms=elapsed_ms,
            )
            raise

    async def get_by_username(self, username: str) -> Optional[UserDB]:
        start = time.perf_counter()
        try:
            user_doc = await self.collection.find_one({"username": username})

            elapsed_ms = int((time.perf_counter() - start) * 1000)
            if user_doc:
                self.logger.info(
                    "mongo_user_find_one_by_username_found",
                    elapsed_ms=elapsed_ms,
                )
                return self.map_to_model(user_doc)
            self.logger.info(
                "mongo_user_find_one_by_username_not_found",
                elapsed_ms=elapsed_ms,
            )
            return None

        except PyMongoError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception(
                "mongo_user_find_one_by_username_error",
                error=str(e),
                elapsed_ms=elapsed_ms,
            )
            raise
