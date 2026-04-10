from typing import List, Optional
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.review_models import Review, ReviewCreate, ReviewInsert, ReviewUpdate
from app.repositories.review_repository import ReviewRepository
from pymongo.results import DeleteResult

import structlog

logger = structlog.get_logger().bind(service="ReviewService")


class ReviewService:
    def __init__(
        self,
        review_repository: ReviewRepository,
    ):
        self.review_repository = review_repository

    async def create_review(
        self, review_request: ReviewCreate, entry_id: str, user_id: str
    ) -> Review:

        review_data = ReviewInsert(
            **review_request.model_dump(),
            user_id=user_id,
            user_media_entry_id=entry_id,
        )
        result = await self.review_repository.create_review(review_data)

        logger.info(
            "review_created",
            user_media_entry_id=entry_id,
            review_id=result.id,
            user_id=user_id,
        )
        return Review.from_db(result)

    async def update_review(
        self, review_id: str, entry_id: str, update_request: ReviewUpdate, user_id: str
    ) -> Optional[Review]:

        updated_review = await self.review_repository.update_review(
            review_id, entry_id, update_request, user_id
        )

        if updated_review is None:
            raise RuntimeError("Review missing after update - data integrity issue")

        logger.info("review_updated", review_id=review_id, user_id=user_id)
        return Review.from_db(updated_review)

    async def delete_review(
        self, entry_id: str, review_id: str, user_id: str
    ) -> None:

        result: DeleteResult = await self.review_repository.delete_review(
            review_id, user_id, entry_id
        )
        if not result.acknowledged:
            raise RuntimeError(f"Failed to delete review {review_id}")

        logger.info("review_deleted", review_id=review_id, user_id=user_id)

    async def get_reviews_for_user_media_entry(
        self, entry_id: str, user_id: str
    ) -> Optional[List[Review]]:

        reviews = (
            await self.review_repository.get_reviews_by_user_media_entry_id_and_user_id(
                entry_id, user_id
            )
        )
        logger.info(
            "reviews_fetched",
            user_media_entry_id=entry_id,
            user_id=user_id,
        )
        if not reviews:
            return None

        return [Review.from_db(review) for review in reviews]

    async def get_review_by_id(
        self, review_id: str, user_id: str, entry_id: str
    ) -> Review:

        try:
            res = await self.review_repository.get_review_by_id(
                review_id, user_id, entry_id
            )
            if res is None:
                raise NotFoundException(f"Review {review_id} not found")
            return Review.from_db(res)
        except Exception:
            raise NotFoundException(f"Review {review_id} not found")

    async def count_reviews_for_user_media_entry(
        self, user_media_entry_id: str, user_id: str
    ) -> int:
        return await self.review_repository.count_reviews_by_user_media_entry_id(
            user_media_entry_id, user_id
        )

    async def delete_reviews_for_user_media_entry(
        self, user_media_entry_id: str, user_id: str
    ) -> None:
        result: DeleteResult = (
            await self.review_repository.delete_reviews_by_user_media_entry_id(
                user_media_entry_id, user_id
            )
        )
        if not result.acknowledged:
            raise RuntimeError(
                f"Failed to delete reviews for entry id: {user_media_entry_id}"
            )
        logger.info(
            "reviews_deleted",
            user_media_entry_id=user_media_entry_id,
            user_id=user_id,
            deleted_count=result.deleted_count,
        )

    async def delete_all_reviews_for_user(self, user_id: str) -> None:
        result: DeleteResult = await self.review_repository.delete_by_user_id(user_id)
        if not result.acknowledged:
            raise RuntimeError(
                f"Deleting all reviews for user is not acknowledged {user_id}"
            )

        logger.info(
            "reviews_deleted_by_user",
            user_id=user_id,
            deleted_count=result.deleted_count,
        )
