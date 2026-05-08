from typing import List, Optional

from app.core.exceptions import (
    InternalServerErrorException,
    NotFoundException,
)
from app.models.db.review_models import (
    ReviewCreate,
    ReviewDB,
    ReviewInsert,
    ReviewUpdate,
)
from app.repositories.review_repository import ReviewRepository

import structlog

logger = structlog.get_logger()


class ReviewService:
    def __init__(
        self,
        review_repository: ReviewRepository,
    ):
        self.repository = review_repository
        self.logger = logger.bind(service="ReviewService")

    async def create_review(
        self,
        review_request: ReviewCreate,
        entry_id: str,
        user_id: str,
    ) -> ReviewDB:
        review_data = ReviewInsert(
            **review_request.model_dump(),
            user_id=user_id,
            user_media_entry_id=entry_id,
        )
        result = await self.repository.insert_review(review_data)
        if result is None:
            raise InternalServerErrorException("Failed to create review")
        self.logger.info(
            "review_created",
            review_id=result.id,
            user_id=user_id,
            entry_id=entry_id,
        )
        return result

    async def update_review(
        self,
        review_id: str,
        entry_id: str,
        update_request: ReviewUpdate,
        user_id: str,
    ) -> Optional[ReviewDB]:

        updated_review = await self.repository.update_review(
            review_id, entry_id, update_request, user_id
        )

        if updated_review is None:
            raise NotFoundException("Review not found")
        self.logger.info(
            "review_updated",
            review_id=review_id,
            user_id=user_id,
            entry_id=entry_id,
        )
        return updated_review

    async def delete_review(self, entry_id: str, review_id: str, user_id: str) -> None:
        deleted = await self.repository.delete_review(review_id, user_id, entry_id)
        if not deleted:
            raise NotFoundException("Review not found")

        self.logger.info(
            "review_deleted",
            review_id=review_id,
            user_id=user_id,
            entry_id=entry_id,
        )

    async def get_reviews_for_user_media_entry(
        self, entry_id: str, user_id: str
    ) -> List[ReviewDB]:
        return await self.repository.get_reviews_by_user_media_entry_id_and_user_id(
            entry_id, user_id
        )

    async def get_review_by_id(
        self, review_id: str, user_id: str, entry_id: str
    ) -> ReviewDB:

        res = await self.repository.get_review_by_id_and_entry_id_and_user_id(review_id, user_id, entry_id)
        if res is None:
            raise NotFoundException(f"Review not found")
        return res

    async def count_reviews_for_user_media_entry(
        self, entry_id: str, user_id: str
    ) -> int:

        return await self.repository.count_reviews_by_user_media_entry_id(
            entry_id, user_id
        )

    async def delete_reviews_for_user_media_entry(
        self, entry_id: str, user_id: str
    ) -> None:
        await self.repository.delete_reviews_by_user_media_entry_id(entry_id, user_id)

        self.logger.info(
            "reviews_deleted",
            user_media_entry_id=entry_id,
            user_id=user_id,
        )

    async def delete_all_reviews_for_user(self, user_id: str) -> None:
        await self.repository.delete_reviews_by_user_id(user_id)

        self.logger.info(
            "all_reviews_deleted_for_user",
            user_id=user_id,
        )
