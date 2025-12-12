import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Path, Query

from app.models.review_models import ReviewCreate, ReviewUpdate
from app.models.user_models import UserData
from app.services.library_service import LibraryService
from app.services.review_service import ReviewService
from app.auth.auth_dependencies import get_current_user

logger = logging.getLogger("review_router")
logging.basicConfig(level=logging.INFO)

# Dependency provider function
def get_review_service():
    return ReviewService()

review_router = APIRouter(prefix="/review")

@review_router.post("/create")
async def create_review(
    review_request: ReviewCreate,
    current_user: UserData = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    try:
        response = review_service.create_review(review_request, current_user)
        logger.info(f"Review created for user {current_user.id}, media {review_request.media_id} :  {response}")
        return response.data
    except ValueError as ve:
        logger.warning(f"Validation error in create_review: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in create_review: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@review_router.put("/update")
async def update_review(
    update_request: ReviewUpdate,
    current_user: UserData = Depends(get_current_user), 
    review_service: ReviewService = Depends(get_review_service)
):
    try:
        response = review_service.update_review(update_request, current_user)
        logger.info(f"Review {update_request.id} updated by user {current_user.id} :  {response}")
        return response.data
    except ValueError as ve:
        logger.warning(f"Validation error in update_review: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in update_review: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@review_router.delete("/delete/{review_id}")
async def delete_review(
    review_id: str,
    current_user: UserData = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    try:
        response = review_service.delete_review(review_id, current_user)
        logger.info(f"Review {review_id} deleted by user {current_user.id} :  {response}")
        return response.data
    except ValueError as ve:
        logger.warning(f"Validation error in delete_review: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in delete_review: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@review_router.get("/{review_id}")
async def get_review_by_id(
    review_id: str = Path(..., description="ID of the review"),
    current_user: UserData = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Get the review data for the current user and a specific review ID.
    """
    try:
        response = review_service.get_review_by_id(current_user.id, review_id) # type: ignore
        logger.info(f"Fetched review with id {review_id} for user {current_user.id}: {response}")
        return response.data
    except ValueError as ve:
        logger.warning(f"Validation error in get_review_by_id: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in get_review_by_id: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")