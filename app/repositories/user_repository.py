from pymongo import ReturnDocument
import structlog
from typing import Optional
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from app.models.user_models import UserDB, UserInsert, UserUpdate
from app.repositories._repo_observability import run_db_op

logger = structlog.get_logger()


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = db[collection_name]
        self.logger = logger.bind(
            repository="UserRepository", collection=collection_name
        )
    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [
                ("username", 1),
            ],
            unique=True,
            name="username_unique_idx",
        )
        
    async def create(self, user: UserInsert) -> UserDB:
        data = user.model_dump()

        async def _op() -> InsertOneResult:
            return await self.collection.insert_one(data)
        try:
            
            result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_insert_one",
            error_event="mongo_user_insert_one_error",
            context={"username": user.username},
        )
            
            return UserDB(**{**data, "_id": result.inserted_id})
        except DuplicateKeyError:
            self.logger.warning(
                "mongo_user_media_entry_insert_duplicate",
                username=user.username,
            )
            raise
            

    async def update(self, id: str, update_data: UserUpdate) -> Optional[UserDB]:
        update_dict = update_data.to_update_dict()

        async def _op() -> UpdateResult:
            return await self.collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_update_query",
            error_event="mongo_user_update_one_error",
            context={"user_id": id},
        )

        if doc:
            self.logger.info(
                "mongo_user_update_success",
                user_id=id,
            )
            return UserDB.model_validate(doc)

        self.logger.warning(
            "mongo_user_update_not_found_or_forbidden",
            user_id=id,
        )
        return None

    async def delete(self, user_id: str) -> DeleteResult:
        async def _op() -> DeleteResult:
            return await self.collection.delete_one({"_id": ObjectId(user_id)})

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_delete_query",
            error_event="mongo_user_delete_one_error",
            context={"user_id": user_id},
        )

        if result.deleted_count == 0:
            self.logger.warning(
                "mongo_user_delete_not_found_or_forbidden",
                user_id=user_id,
            )
        else:
            self.logger.info(
                "mongo_user_delete_success",
                user_id=user_id,
                deleted_count=result.deleted_count,
            )
        return result

    async def get_by_id(self, id: str) -> Optional[UserDB]:
        async def _op():
            return await self.collection.find_one({"_id": ObjectId(id)})

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_find_one_by_id_query",
            error_event="mongo_user_find_one_by_id_error",
            context={"user_id": id},
        )

        if doc:
            self.logger.info("mongo_user_find_one_by_id_found", user_id=id)
            return UserDB.model_validate(doc)
        self.logger.info("mongo_user_find_one_by_id_not_found", user_id=id)
        return None

    async def is_username_exists(self, username: str) -> bool:
        async def _op():
            return await self.collection.find_one({"username": username})

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_find_one_by_username_query",
            error_event="mongo_user_find_one_by_username_error",
            context={"username": username},
        )

        exists = doc is not None
        self.logger.info(
            "mongo_user_find_one_by_username_exists",
            username=username,
            exists=exists,
        )
        return exists

    async def get_by_username(self, username: str) -> Optional[UserDB]:
        async def _op():
            return await self.collection.find_one({"username": username})

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_find_one_by_username_query",
            error_event="mongo_user_find_one_by_username_error",
            context={"username": username},
        )

        if doc:
            self.logger.info(
                "mongo_user_find_one_by_username_found",
                username=username,
            )
            return UserDB.model_validate(doc)
        self.logger.info(
            "mongo_user_find_one_by_username_not_found",
            username=username,
        )
        return None
