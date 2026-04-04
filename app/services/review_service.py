from datetime import datetime, timezone
from typing import List, Optional
import structlog
from app.core.event_bus import EventBus
from app.core.exceptions import ForbiddenException, NotFoundException
from app.repositories.review_repository import ReviewRepository
from app.models.review_models import (
    ReviewCreate,
    ReviewDB,
    ReviewInsert,
    ReviewUpdate,
)
from pymongo.results import InsertOneResult, DeleteResult

logger = structlog.get_logger().bind(service="ReviewService")


class ReviewService:
    def __init__(self, review_repository: ReviewRepository, event_bus: EventBus):
        self.repository = review_repository
        self.event_bus = event_bus

    async def create_review(
        self, review_request: ReviewCreate, user_id: str
    ) -> ReviewDB:

        review_data = ReviewInsert(**review_request.model_dump(), userId=user_id)

        result: InsertOneResult = await self.repository.create_review(review_data)
        logger.info(
            "Review created",
            user_media_entry_id=review_request.user_media_entry_id,
            review_id=str(result.inserted_id),
        )
        await self.event_bus.publish(
            "review.changed",
            review_id=str(result.inserted_id),
            user_media_entry_id=str(review_request.user_media_entry_id),
            occurred_at=review_data.created_at,
        )

        return ReviewDB(id=str(result.inserted_id), **review_data.model_dump())

    async def update_review(
        self, review_id: str, update_request: ReviewUpdate, user_id: str
    ) -> Optional[ReviewDB]:
        review = await self._verify_ownership(review_id, user_id)

        update_dict = update_request.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.now(timezone.utc)

        await self.repository.update_review(review_id, update_dict)
        logger.info("Review updated", review_id=review_id)
        updated_review = await self.repository.get_review_by_id(review_id)

        if updated_review is None:
            raise RuntimeError("Review missing after update - data integrity issue")

        await self.event_bus.publish(
            "review.changed",
            review_id=str(updated_review.id),
            user_media_entry_id=str(updated_review.user_media_entry_id),
            occurred_at=datetime.now(timezone.utc),
        )

        return updated_review

    async def delete_review(self, review_id: str, user_id: str) -> bool:
        await self._verify_ownership(review_id, user_id)
        result: DeleteResult = await self.repository.delete_review(review_id)

        if not result.acknowledged:
            raise RuntimeError(f"Failed to delete review {review_id}")
        
        logger.info("review_deleted", review_id=review_id, user_id=user_id)
        await self.event_bus.publish(
            "review.deleted",
            review_id=review_id,
            user_id=user_id,
            occurred_at=datetime.now(timezone.utc),
        )
        return result.acknowledged

    async def get_reviews_for_user_media_entry(
        self, user_media_entry_id: str
    ) -> Optional[List[ReviewDB]]:
        reviews = await self.repository.get_reviews_by_user_media_entry_id(
            user_media_entry_id
        )
        logger.info("reviews_fetched", user_media_entry_id=user_media_entry_id)
        return reviews or []

    async def get_review_by_id(self, review_id: str) -> ReviewDB:
        review = await self.repository.get_review_by_id(review_id)
        if not review:
            raise NotFoundException(f"Review {review_id} not found")
        return review

    async def count_reviews_for_user_media_entry(
        self, user_media_entry_id: str
    ) -> int:
        return await self.repository.count_reviews_by_user_media_entry_id(
            user_media_entry_id
        )

    async def delete_reviews_for_user_media_entry(
        self, user_media_entry_id: str
    ) -> bool:
        result: DeleteResult = (
            await self.repository.delete_reviews_by_user_media_entry_id(
                user_media_entry_id
            )
        )
        logger.info(
            "reviews_deleted",
            user_media_entry_id=user_media_entry_id,
            deleted_count=result.deleted_count,
        )
        return result.acknowledged

    async def delete_all_reviews_for_user(self, user_id: str) -> bool:
        result: DeleteResult = await self.repository.delete_by_user_id(user_id)
        logger.info(
            "reviews_deleted_by_user",
            user_id=user_id,
            deleted_count=result.deleted_count,
        )
        return result.acknowledged

    async def _verify_ownership(self, review_id: str, user_id: str) -> ReviewDB:
        review = await self.repository.get_review_by_id(review_id)
        if not review:
            raise NotFoundException(f"Review {review_id} not found")
        if review.user_id != user_id:
            logger.warning(
                "unauthorized_access_attempt", user_id=user_id, review_id=review_id
            )
            raise ForbiddenException("You do not have access to this review")
        return review
