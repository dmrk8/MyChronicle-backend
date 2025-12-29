from datetime import datetime
import structlog
from app.repositories.review_repository import ReviewRepository
from app.models.review_models import ReviewCreate, ReviewDB, ReviewUpdate, ReviewResponse
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

logger = structlog.get_logger().bind(service="ReviewService")


class ReviewService:
    def __init__(self, review_repository: ReviewRepository):
        self.repository = review_repository

    async def create_review(self, review_request: ReviewCreate) -> ReviewResponse:
        if review_request.rating is not None and (
            review_request.rating < 0 or review_request.rating > 10
        ):
            raise ValueError("Rating must be between 0 and 10")

        if review_request.review is not None and len(review_request.review) > 5000:
            raise ValueError("Review must be less than 5000 characters")

        review_data = ReviewDB(
            **review_request.model_dump()  
        )

        try:
            result: InsertOneResult = await self.repository.create_review(review_data)
            logger.info(
                "Review created",
                user_media_entry_id=review_request.user_media_entry_id,
                review_id=str(result.inserted_id),
            )
            return ReviewResponse(
                message="Review created successfully",
                review_id=str(result.inserted_id),  # type: ignore
                acknowledged=result.acknowledged,
            )
        except Exception as e:
            logger.error(
                "Error creating review",
                user_media_entry_id=review_request.user_media_entry_id,
                error=str(e),
            )
            raise

    async def update_review(self, review_id: str, update_request: ReviewUpdate) -> ReviewResponse:
        review_data = await self.repository.get_review_by_id(review_id)
        if not review_data:
            logger.error("Review not found", review_id=review_id)
            raise ValueError(f"Review with id {review_id} not found")

        if update_request.rating is not None and (
            update_request.rating < 0 or update_request.rating > 10
        ):
            logger.warning("Invalid rating", rating=update_request.rating)
            raise ValueError("Rating must be between 0 and 10")

        if update_request.review is not None and len(update_request.review) > 5000:
            logger.warning("Review text too long")
            raise ValueError("Review must be less than 5000 characters")

        if update_request.review_progress is not None:
            if update_request.review_progress < 0 or update_request.review_progress > 10000:
                logger.warning(
                    "Invalid review progress", review_progress=update_request.review_progress
                )
                raise ValueError("Review progress must be between 0 and 10000")

        if update_request.written_at is not None:
            if update_request.written_at > datetime.now():
                logger.warning(
                    "Written at date is in the future", written_at=update_request.written_at
                )
                raise ValueError("Written at date cannot be in the future")

        try:
            update_dict = update_request.model_dump(exclude_unset=True)
            update_dict["updated_at"] = datetime.now()
            result: UpdateResult = await self.repository.update_review(review_id, update_dict)
            logger.info("Review updated", review_id=review_id)
            return ReviewResponse(
                message="Review updated successfully",
                review_id=review_id,  # type: ignore
                acknowledged=result.acknowledged,
            )
        except Exception as e:
            logger.error("Error updating review", error=str(e))
            raise

    async def delete_review(self, review_id: str) -> ReviewResponse:
        review_data = await self.repository.get_review_by_id(review_id)
        if not review_data:
            raise ValueError(f"Review with id {review_id} not found")

        try:
            result: DeleteResult = await self.repository.delete_review(review_id)
            logger.info("Review deleted", review_id=review_id)
            return ReviewResponse(
                message="Review deleted successfully",
                review_id=review_id,  # type: ignore
                acknowledged=result.acknowledged,
            )
        except Exception as e:
            logger.error("Error deleting review", error=str(e))
            raise

    async def get_reviews_by_user_media_entry_id(self, user_media_entry_id: str) -> ReviewResponse:
        try:
            reviews = await self.repository.get_reviews_by_user_media_entry_id(user_media_entry_id)
            if reviews is None:
                return ReviewResponse(message="No reviews found", data=None)  # type: ignore
            logger.info("Fetched reviews", user_media_entry_id=user_media_entry_id)
            return ReviewResponse(message="Reviews fetched successfully", data=reviews)  # type: ignore
        except Exception as e:
            logger.error(
                "Error fetching reviews", user_media_entry_id=user_media_entry_id, error=str(e)
            )
            raise

    async def get_review_by_id(self, review_id: str) -> ReviewResponse:
        try:
            review_data = await self.repository.get_review_by_id(review_id)
            if not review_data:
                raise ValueError("Review not found")
            logger.info("Review fetched successfully", review_id=review_id)
            return ReviewResponse(message="Review fetched successfully", data=review_data)  # type: ignore
        except Exception as e:
            logger.error("Error finding review by id", review_id=review_id, error=str(e))
            raise

    async def count_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str
    ) -> ReviewResponse:
        try:
            count = await self.repository.count_reviews_by_user_media_entry_id(user_media_entry_id)
            logger.info("Counted reviews", user_media_entry_id=user_media_entry_id)
            return ReviewResponse(message="Review count fetched successfully", data=count)  # type: ignore
        except Exception as e:
            logger.error(
                "Error counting reviews", user_media_entry_id=user_media_entry_id, error=str(e)
            )
            raise
