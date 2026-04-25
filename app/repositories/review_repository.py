from typing import List, Optional
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult, DeleteResult
from bson import ObjectId
from app.models.db.db_context_model import DBOpContext
from app.models.db.review_models import ReviewDB, ReviewInsert, ReviewUpdate
from app.repositories._repo_observability import run_db_op
import structlog

logger = structlog.get_logger()


class ReviewRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = self.db[collection_name]
        self.logger = logger.bind(
            repository="ReviewRepository", collection=collection_name
        )

    async def insert_review(self, review_data: ReviewInsert) -> ReviewDB:
        context = DBOpContext(
            user_id=review_data.user_id,
            entry_id=review_data.user_media_entry_id,
            operation="insert_one",
            collection=self.collection.name,
        )

        data = review_data.model_dump()

        async def _op() -> InsertOneResult:
            return await self.collection.insert_one(data)

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_insert_one",
            error_event="mongo_review_insert_one_error",
            context=context,
        )
        return ReviewDB.model_validate({**data, "_id": result.inserted_id})

    async def delete_review(
        self,  review_id: str, user_id: str, user_media_entry_id: str
    ) -> bool:
        context = DBOpContext(
            review_id=review_id,
            user_id=user_id,
            entry_id=user_media_entry_id,
            operation="delete_one",
            collection=self.collection.name,
        )

        async def _op() -> DeleteResult:
            return await self.collection.delete_one(
                {
                    "_id": ObjectId(review_id),
                    "user_id": user_id,
                    "user_media_entry_id": user_media_entry_id,
                }
            )

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_delete_one",
            error_event="mongo_review_delete_one_error",
            context=context,
        )
        return result.deleted_count > 0

    async def update_review(
        self,
        review_id: str,
        user_media_entry_id: str,
        update: ReviewUpdate,
        user_id: str,
    ) -> Optional[ReviewDB]:
        context = DBOpContext(
            review_id=review_id,
            user_id=user_id,
            entry_id=user_media_entry_id,
            operation="find_one_and_update",
            collection=self.collection.name,
        )
        update_dict = update.to_update_dict()

        async def _op():
            return await self.collection.find_one_and_update(
                {
                    "_id": ObjectId(review_id),
                    "user_id": user_id,
                    "user_media_entry_id": user_media_entry_id,
                },
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_update_one",
            error_event="mongo_review_update_one_error",
            context=context,
        )
        if not doc:
            return ReviewDB.model_validate(doc)
        return None

    async def get_reviews_by_user_media_entry_id_and_user_id(
        self, user_media_entry_id: str, user_id: str
    ) -> Optional[List[ReviewDB]]:
        context = DBOpContext(
            user_id=user_id,
            entry_id=user_media_entry_id,
            operation="find",
            collection=self.collection.name,
        )

        async def _op() -> List[ReviewDB]:
            cursor = self.collection.find(
                {"user_media_entry_id": user_media_entry_id, "user_id": user_id}
            )
            return [ReviewDB(**doc) async for doc in cursor]

        results = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_find_by_user_media_entry_id",
            error_event="mongo_review_find_by_user_media_entry_id_error",
            context=context,
        )
        return results

    async def get_review_by_id(
        self, review_id: str, user_id: str, user_media_entry_id: str
    ) -> Optional[ReviewDB]:
        context = DBOpContext(
            review_id=review_id,
            user_id=user_id,
            entry_id=user_media_entry_id,
            operation="find_one",
            collection=self.collection.name,
        )

        async def _op():
            return await self.collection.find_one(
                {
                    "_id": ObjectId(review_id),
                    "user_id": user_id,
                    "user_media_entry_id": user_media_entry_id,
                }
            )

        data = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_find_one_by_id_query",
            error_event="mongo_review_find_one_by_id_error",
            context=context,
        )

        if data:
            ReviewDB.model_validate(data)
        return None

    async def count_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str, user_id: str
    ) -> int:
        context = DBOpContext(
            user_id=user_id,
            entry_id=user_media_entry_id,
            operation="count",
            collection=self.collection.name,
        )

        async def _op() -> int:
            return await self.collection.count_documents(
                {"user_media_entry_id": user_media_entry_id, "user_id": user_id}
            )

        count = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_count_by_user_media_entry_id",
            error_event="mongo_review_count_by_user_media_entry_id_error",
            context=context,
        )

        return count

    async def delete_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str, user_id: str
    ) -> bool:
        context = DBOpContext(
            user_id=user_id,
            entry_id=user_media_entry_id,
            operation="delete_many",
            collection=self.collection.name,
        )

        async def _op() -> DeleteResult:
            return await self.collection.delete_many(
                {"user_media_entry_id": user_media_entry_id, "user_id": user_id}
            )

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_delete_many_by_user_media_entry_id",
            error_event="mongo_review_delete_many_by_user_media_entry_id_error",
            context=context,
        )
        return result.deleted_count > 0

    async def delete_by_user_id(self, user_id: str) -> bool:
        context = DBOpContext(
            user_id=user_id,
            operation="delete_many",
            collection=self.collection.name,
        )

        async def _op() -> DeleteResult:
            return await self.collection.delete_many({"user_id": user_id})

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_delete_many",
            error_event="mongo_review_delete_many_error",
            context=context,
        )

        return result.deleted_count > 0
