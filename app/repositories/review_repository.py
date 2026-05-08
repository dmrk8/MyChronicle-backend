from typing import List, Optional
from bson import ObjectId
from app.models.db.review_models import ReviewDB, ReviewInsert, ReviewUpdate
from app.repositories._base_repository import CRUDRepository


class ReviewRepository(CRUDRepository[ReviewDB, ReviewInsert, ReviewUpdate]):
    db_model = ReviewDB

    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [
                ("user_media_entry_id", 1),
                ("user_id", 1),
            ],
            name="user_media_entry_id_user_id_idx",
        )
        await self.collection.create_index([("user_id", 1)], name="user_id_idx")

    async def insert_review(self, review_data: ReviewInsert) -> ReviewDB:
        return await self._insert(
            review_data,
            self._make_context(
                operation="insert_one",
                user_id=review_data.user_id,
                entry_id=review_data.user_media_entry_id,
            ),
        )

    async def delete_review(
        self, review_id: str, user_id: str, user_media_entry_id: str
    ) -> bool:
        return await self._delete_one(
            {
                "_id": ObjectId(review_id),
                "user_id": user_id,
                "user_media_entry_id": user_media_entry_id,
            },
            self._make_context(
                operation="delete_one",
                user_id=user_id,
                entry_id=user_media_entry_id,
                review_id=review_id,
            ),
        )

    async def update_review(
        self,
        review_id: str,
        user_media_entry_id: str,
        update: ReviewUpdate,
        user_id: str,
    ) -> Optional[ReviewDB]:
        return await self._find_one_and_update(
            {
                "_id": ObjectId(review_id),
                "user_id": user_id,
                "user_media_entry_id": user_media_entry_id,
            },
            update,
            self._make_context(
                operation="find_one_and_update",
                user_id=user_id,
                entry_id=user_media_entry_id,
                review_id=review_id,
            ),
        )

    async def get_reviews_by_user_media_entry_id_and_user_id(
        self, user_media_entry_id: str, user_id: str
    ) -> List[ReviewDB]:
        return await self._find_many(
            {"user_media_entry_id": user_media_entry_id, "user_id": user_id},
            self._make_context(
                operation="find",
                user_id=user_id,
                entry_id=user_media_entry_id,
            ),
        )

    async def get_review_by_id_and_entry_id_and_user_id(
        self, review_id: str, user_id: str, user_media_entry_id: str
    ) -> Optional[ReviewDB]:
        return await self._find_one(
            {
                "_id": ObjectId(review_id),
                "user_id": user_id,
                "user_media_entry_id": user_media_entry_id,
            },
            self._make_context(
                operation="find_one",
                user_id=user_id,
                entry_id=user_media_entry_id,
                review_id=review_id,
            ),
        )

    async def count_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str, user_id: str
    ) -> int:
        return await self._count(
            {"user_media_entry_id": user_media_entry_id, "user_id": user_id},
            self._make_context(
                operation="count",
                user_id=user_id,
                entry_id=user_media_entry_id,
            ),
        )

    async def delete_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str, user_id: str
    ) -> bool:
        return await self._delete_many(
            {"user_media_entry_id": user_media_entry_id, "user_id": user_id},
            self._make_context(
                operation="delete_many",
                user_id=user_id,
                entry_id=user_media_entry_id,
            ),
        )

    async def delete_reviews_by_user_id(self, user_id: str) -> bool:
        return await self._delete_many(
            {"user_id": user_id},
            self._make_context(
                operation="delete_many",
                user_id=user_id,
            ),
        )
