from fastapi import APIRouter, Depends, Path, status

from app.models.review_models import ReviewCreate, ReviewUpdate
from app.models.user_models import UserDB
from app.services.review_service import ReviewService
from app.auth.auth_dependencies import get_current_user
from app.core.dependencies import get_review_service

review_router = APIRouter(prefix="/reviews")


@review_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_review(
    review_request: ReviewCreate,
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.create_review(review_request, user_id=current_user.id)


@review_router.patch("/{review_id}")
async def update_review(
    update_request: ReviewUpdate,
    review_id: str = Path(..., description="ID of the review"),
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.update_review(
        review_id, update_request, current_user.id
    )


@review_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.delete_review(review_id, current_user.id)


@review_router.get("/entry/{user_media_entry_id}")
async def get_reviews_by_user_media_entry_id(
    user_media_entry_id: str = Path(..., description="ID of the user media entry"),
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Get all reviews for a specific user media entry.
    """
    return await review_service.get_reviews_for_user_media_entry(user_media_entry_id)
