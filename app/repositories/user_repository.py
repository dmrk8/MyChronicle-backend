from pymongo import ReturnDocument
import structlog
from typing import Optional
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from app.models.db.db_context_model import DBOpContext
from app.models.db.user_models import UserDB, UserInsert, UserUpdate
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

    async def insert_user(self, user: UserInsert) -> UserDB:
        context = DBOpContext(
            username=user.username,
            operation="insert_one",
            collection=self.collection.name,
        )
        data = user.model_dump()

        async def _op() -> InsertOneResult:
            return await self.collection.insert_one(data)

        try:

            result = await run_db_op(
                self.logger,
                _op,
                success_event="mongo_user_insert_one",
                error_event="mongo_user_insert_one_error",
                context=context,
            )

            return UserDB(**{**data, "_id": result.inserted_id})
        except DuplicateKeyError:
            raise

    async def update(
        self, id: str, update_data: UserUpdate
    ) -> Optional[UserDB]:
        context = DBOpContext(
            user_id=id,
            operation="update_one",
            collection=self.collection.name,
        )

        update_dict = update_data.to_update_dict()

        async def _op():
            return await self.collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER,
            )
        try:
            doc = await run_db_op(
                self.logger,
                _op,
                success_event="mongo_user_update_query",
                error_event="mongo_user_update_one_error",
                context=context,
            )
        except DuplicateKeyError:
            raise 

        if doc:
            return UserDB.model_validate(doc)

        return None

    async def delete(self, user_id: str) -> bool:
        context = DBOpContext(
            user_id=user_id,
            operation="delete_one",
            collection=self.collection.name,
        )

        async def _op() -> DeleteResult:
            return await self.collection.delete_one({"_id": ObjectId(user_id)})

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_delete_query",
            error_event="mongo_user_delete_one_error",
            context=context,
        )

        return result.deleted_count > 0

    async def get_by_id(self, id: str) -> Optional[UserDB]:
        context = DBOpContext(
            user_id=id,
            operation="find_one",
            collection=self.collection.name,
        )

        async def _op():
            return await self.collection.find_one({"_id": ObjectId(id)})

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_find_one_by_id_query",
            error_event="mongo_user_find_one_by_id_error",
            context=context,
        )

        if doc:
            return UserDB.model_validate(doc)
        return None

    async def get_by_username(
        self, username: str
    ) -> Optional[UserDB]:
        context = DBOpContext(
            username=username,
            operation="find_one",
            collection=self.collection.name,
        )

        async def _op():
            return await self.collection.find_one({"username": username})

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_user_find_one_by_username_query",
            error_event="mongo_user_find_one_by_username_error",
            context=context,
        )

        if doc:
            return UserDB.model_validate(doc)
        return None
