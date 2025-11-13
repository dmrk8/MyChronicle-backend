from datetime import datetime
import logging
from app.repositories.review_repository import ReviewsCRUD 
from app.models.review_models import ReviewCreate, ReviewDB, ReviewUpdate, ReviewResponse
from app.models.user_models import UserData

logger = logging.getLogger("review_service")
logging.basicConfig(level=logging.INFO)

class ReviewService:
    def __init__(self):
        self.repository = ReviewsCRUD()

    def create_review(self, review_request : ReviewCreate, user_data: UserData) -> ReviewResponse:
        if not user_data.id:
            logger.error("User ID cannot be None.")
            raise ValueError("User ID cannot be None.")
    
        existing_review = self.repository.get_review_by_user_and_media(
            user_id=user_data.id, media_id=review_request.media_id
        )

        if existing_review:
            logger.warning(f"Review already exists for user {user_data.id} and media {review_request.media_id}")
            raise ValueError("record already exists")
        if review_request.rating is not None and (review_request.rating < 0 or review_request.rating > 10):
            logger.warning(f"Invalid rating {review_request.rating} for user {user_data.id}")
            raise ValueError("rating must be between 0 and 10")
        
        if review_request.review is not None and len(review_request.review) > 5000:
            logger.warning(f"Review text too long for user {user_data.id}")
            raise ValueError("Review must be less than 5000 characters")

        review_data = ReviewDB( 
            user_id=user_data.id, # type: ignore
            media_id=review_request.media_id, # type: ignore
            type=review_request.type,
            rating=review_request.rating,
            review=review_request.review,
            is_favorite=review_request.is_favorite, # type: ignore
            created_at=datetime.now(), # type: ignore
            updated_at=datetime.now() # type: ignore
        )

        try:
            response = self.repository.create_review(review_data)
            logger.info(f"Review created for user {user_data.id}, media {review_request.media_id}")
            return response
        except Exception as e:
            logger.error(f"Error creating review in ReviewService: {e}")
            raise
    
    
    def update_review(self, update_request: ReviewUpdate, user: UserData) -> ReviewResponse:
        review_data = self.repository.get_review_by_id(update_request.id)
        
        if not review_data:
            logger.error(f"Review with id {update_request.id} not found for update")
            raise ValueError(f"Review with id {update_request.id} not found")

        if review_data.user_id != user.id:
            logger.warning(f"User {user.id} not authorized to update review {update_request.id}")
            raise ValueError("Not authorized")
        
        review_data.updated_at = datetime.now()
        review_data.review = update_request.review or ""
        review_data.rating = update_request.rating or 0.0

        try:
            response = self.repository.update_review(review_data)
            logger.info(f"Review {update_request.id} updated by user {user.id}")
            return response
        except Exception as e:
            logger.error(f"Error updating review in ReviewService: {e}")
            raise
             
    def delete_review(self, review_id: str, user: UserData) -> ReviewResponse:
        review_data = self.repository.get_review_by_id(review_id)

        if not review_data:
            logger.error(f"Review with id {review_id} not found for deletion")
            raise ValueError(f"Review with id {review_id} not found")

        if review_data.user_id != user.id:
            logger.warning(f"User {user.id} not authorized to delete review {review_id}")
            raise ValueError("not authorized")

        try:
            response = self.repository.delete_review(review_id)
            logger.info(f"Review {review_id} deleted by user {user.id}")
            return response
        except Exception as e:
            logger.error(f"Error deleting review in ReviewService: {e}")
            raise
        
    def get_reviews_by_userid(self, user: UserData) -> ReviewResponse:
        if not user.id:
            logger.error("User ID cannot be None.")
            raise ValueError("User ID cannot be None.")
        
        try:
            review_list = self.repository.get_reviews_by_userid(user.id)
            logger.info(f"Fetched {len(review_list)} reviews for user {user.id}")
            return ReviewResponse(
                message="Reviews fetched successfully", # type: ignore
                data=review_list # type: ignore
            )
        except Exception as e:
            logger.error(f"Error fetching reviews for user {user.id}: {e}")
            raise







