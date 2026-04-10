from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from bson import ObjectId
from app.models.review_models import ReviewDB, ReviewInsert, ReviewUpdate
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

    async def is_exists(self, review_id: str, user_id: str, user_media_entry_id: str) -> bool:
        async def _op() -> int:
            return await self.collection.count_documents(
                {"_id": ObjectId(review_id), "user_id": user_id, "user_media_entry_id": user_media_entry_id}, limit=1
            )

        count = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_exists",
            error_event="mongo_review_exists_error",
            context={"review_id": review_id},
        )
        return count > 0

    async def create_review(self, review_data: ReviewInsert) -> ReviewDB:
        data = review_data.model_dump()

        async def _op() -> InsertOneResult:
            return await self.collection.insert_one(data)

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_insert_one",
            error_event="mongo_review_insert_one_error",
            context={},
        )
        self.logger.info("mongo_review_inserted_id", review_id=str(result.inserted_id))
        return ReviewDB.model_validate({**data, "_id": result.inserted_id})

    async def delete_review(self, review_id: str, user_id: str, user_media_entry_id: str) -> DeleteResult:
        async def _op() -> DeleteResult:
            return await self.collection.delete_one(
                {"_id": ObjectId(review_id), "user_id": user_id, "user_media_entry_id": user_media_entry_id}
            )

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_delete_one",
            error_event="mongo_review_delete_one_error",
            context={"review_id": review_id},
        )
        self.logger.info(
            "mongo_review_delete_one_result",
            review_id=review_id,
            user_id=user_id,
            deleted_count=result.deleted_count,
        )
        return result

    async def update_review(
        self, review_id: str, user_media_entry_id: str, update: ReviewUpdate, user_id: str
    ) -> ReviewDB:

        update_dict = update.to_update_dict()

        async def _op():
            return await self.collection.find_one_and_update(
                {"_id": ObjectId(review_id), "user_id": user_id, "user_media_entry_id": user_media_entry_id},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_update_one",
            error_event="mongo_review_update_one_error",
            context={"review_id": review_id, "user_id": user_id},
        )
        if not doc:
            self.logger.warning(
            "mongo_user_media_entry_update_not_found_or_forbidden",
            review_id=review_id,
            user_id=user_id,
        )

            raise
        self.logger.info(
                "mongo_user_media_entry_update_success",
                review_id=review_id,
                user_id=user_id,
            )
        return ReviewDB.model_validate(doc)

               

    async def get_reviews_by_user_media_entry_id_and_user_id(
        self, user_media_entry_id: str, user_id: str
    ) -> Optional[List[ReviewDB]]:
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
            context={"user_media_entry_id": user_media_entry_id},
        )
        self.logger.info(
            "mongo_review_find_by_user_media_entry_id_result",
            user_media_entry_id=user_media_entry_id,
            user_id=user_id,
            count=len(results),
        )
        return results

    async def get_review_by_id(
        self, review_id: str, user_id: str, user_media_entry_id: str
    ) -> Optional[ReviewDB]:
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
            context={"review_id": review_id},
        )

        if data:
            self.logger.info(
                "mongo_review_find_one_by_id_found",
                review_id=review_id,
                user_id=user_id,
            )
            return ReviewDB(**data)

        self.logger.info(
            "mongo_review_find_one_by_id_not_found",
            review_id=review_id,
            user_id=user_id,
            user_media_entry_id=user_media_entry_id
        )
        return None

    async def count_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str, user_id: str
    ) -> int:
        async def _op() -> int:
            return await self.collection.count_documents(
                {"user_media_entry_id": user_media_entry_id, "user_id": user_id}
            )

        count = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_count_by_user_media_entry_id",
            error_event="mongo_review_count_by_user_media_entry_id_error",
            context={"user_media_entry_id": user_media_entry_id},
        )
        self.logger.info(
            "mongo_review_count_by_user_media_entry_id_result",
            user_media_entry_id=user_media_entry_id,
            user_id=user_id,
            count=count,
        )
        return count

    async def delete_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str, user_id: str
    ) -> DeleteResult:
        async def _op() -> DeleteResult:
            return await self.collection.delete_many(
                {"user_media_entry_id": user_media_entry_id, "user_id": user_id}
            )

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_delete_many_by_user_media_entry_id",
            error_event="mongo_review_delete_many_by_user_media_entry_id_error",
            context={"user_media_entry_id": user_media_entry_id, "user_id": user_id},
        )
        self.logger.info(
            "mongo_review_delete_many_by_user_media_entry_id_result",
            user_media_entry_id=user_media_entry_id,
            user_id=user_id,
            deleted_count=result.deleted_count,
        )
        return result

    async def delete_by_user_id(self, user_id: str) -> DeleteResult:
        async def _op() -> DeleteResult:
            return await self.collection.delete_many({"user_id": user_id})

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_review_delete_many",
            error_event="mongo_review_delete_many_error",
            context={"user_id": user_id},
        )
        self.logger.info(
            "mongo_review_delete_many_result",
            user_id=user_id,
            deleted_count=result.deleted_count,
        )
        return result
