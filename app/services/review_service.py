from datetime import datetime
import logging
from app.repositories.review_repository import ReviewsCRUD
from app.models.review_models import ReviewCreate, ReviewDB, ReviewUpdate, ReviewResponse
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

logger = logging.getLogger("review_service")
logging.basicConfig(level=logging.INFO)


class ReviewService:
    def __init__(self):
        self.repository = ReviewsCRUD()

    def create_review(self, review_request: ReviewCreate) -> ReviewResponse:
        if review_request.rating is not None and (
            review_request.rating < 0 or review_request.rating > 10
        ):
            logger.warning(f"Invalid rating {review_request.rating}")
            raise ValueError("Rating must be between 0 and 10")

        if review_request.review is not None and len(review_request.review) > 5000:
            logger.warning("Review text too long")
            raise ValueError("Review must be less than 5000 characters")

        review_data = ReviewDB(
            **review_request.model_dump(), created_at=datetime.now(), updated_at=datetime.now()  # type: ignore
        )

        try:
            result: InsertOneResult = self.repository.create_review(review_data)
            logger.info(f"Review created for user_media_entry {review_request.user_media_entry_id}")
            return ReviewResponse(
                message="Review created successfully",
                review_id=str(result.inserted_id),  # type: ignore
                acknowledged=result.acknowledged,
            )
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            raise

    def update_review(self, update_request: ReviewUpdate) -> ReviewResponse:
        review_data = self.repository.get_review_by_id(update_request.id)
        if not review_data:
            logger.error(f"Review with id {update_request.id} not found")
            raise ValueError(f"Review with id {update_request.id} not found")

        if update_request.rating is not None and (
            update_request.rating < 0 or update_request.rating > 10
        ):
            logger.warning(f"Invalid rating {update_request.rating}")
            raise ValueError("Rating must be between 0 and 10")

        if update_request.review is not None and len(update_request.review) > 5000:
            logger.warning("Review text too long")
            raise ValueError("Review must be less than 5000 characters")

        if update_request.review_progress is not None:
            if update_request.review_progress < 0 or update_request.review_progress > 10000:
                logger.warning(f"Invalid review progress {update_request.review_progress}")
                raise ValueError("Review progress must be between 0 and 10000")

        if update_request.written_at is not None:
            if update_request.written_at > datetime.now():
                logger.warning(f"Written at date {update_request.written_at} is in the future")
                raise ValueError("Written at date cannot be in the future")

        try:
            result: UpdateResult = self.repository.update_review(update_request)
            logger.info(f"Review {update_request.id} updated")
            return ReviewResponse(
                message="Review updated successfully",
                review_id=update_request.id,  # type: ignore
                matched_count=result.matched_count,  # type: ignore
                modified_count=result.modified_count,  # type: ignore
                acknowledged=result.acknowledged,
                updated_at=datetime.now(),  # type: ignore
            )
        except Exception as e:
            logger.error(f"Error updating review: {e}")
            raise

    def delete_review(self, review_id: str) -> ReviewResponse:
        review_data = self.repository.get_review_by_id(review_id)
        if not review_data:
            logger.error(f"Review with id {review_id} not found")
            raise ValueError(f"Review with id {review_id} not found")

        try:
            result: DeleteResult = self.repository.delete_review(review_id)
            logger.info(f"Review {review_id} deleted")
            return ReviewResponse(
                message="Review deleted successfully",
                review_id=review_id,  # type: ignore
                deleted_count=result.deleted_count,  # type: ignore
                acknowledged=result.acknowledged,
            )
        except Exception as e:
            logger.error(f"Error deleting review: {e}")
            raise

    def get_reviews_by_user_media_entry_id(self, user_media_entry_id: str) -> ReviewResponse:
        try:
            reviews = self.repository.get_reviews_by_user_media_entry_id(user_media_entry_id)
            if reviews is None:
                logger.info(f"No reviews found for user_media_entry {user_media_entry_id}")
                return ReviewResponse(message="No reviews found", data=None)  # type: ignore
            logger.info(
                f"Fetched {len(reviews)} reviews for user_media_entry {user_media_entry_id}"
            )
            return ReviewResponse(message="Reviews fetched successfully", data=reviews)  # type: ignore
        except Exception as e:
            logger.error(f"Error fetching reviews for user_media_entry {user_media_entry_id}: {e}")
            raise

    def get_review_by_id(self, review_id: str) -> ReviewResponse:
        try:
            review_data = self.repository.get_review_by_id(review_id)
            if not review_data:
                logger.info(f"No review found with id {review_id}")
                raise ValueError("Review not found")
            logger.info(f"Found review with id {review_id}")
            return ReviewResponse(message="Review fetched successfully", data=review_data)  # type: ignore
        except Exception as e:
            logger.error(f"Error finding review by id {review_id}: {e}")
            raise

    def count_reviews_by_user_media_entry_id(self, user_media_entry_id: str) -> ReviewResponse:
        try:
            count = self.repository.count_reviews_by_user_media_entry_id(user_media_entry_id)
            logger.info(f"Counted {count} reviews for user_media_entry {user_media_entry_id}")
            return ReviewResponse(message="Review count fetched successfully", data=count)  # type: ignore
        except Exception as e:
            logger.error(f"Error counting reviews for user_media_entry {user_media_entry_id}: {e}")
            raise
