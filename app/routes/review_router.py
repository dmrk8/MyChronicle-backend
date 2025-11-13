import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query

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
        logger.info(f"Review created for user {current_user.id}, media {review_request.media_id}")
        return response
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
        logger.info(f"Review {update_request.id} updated by user {current_user.id}")
        return response
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
        logger.info(f"Review {review_id} deleted by user {current_user.id}")
        return response
    except ValueError as ve:
        logger.warning(f"Validation error in delete_review: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in delete_review: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@review_router.get("/library")
async def get_library(
    media_type: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    sort_by: str = Query("created_at"),
    sort_order: int = Query(1, description="1 for ascending, -1 for descending"),
    title: Optional[str] = Query(None),
    current_user: UserData = Depends(get_current_user)):
    try:
        library_service = LibraryService(media_type)
        response = await library_service.get_user_reviews(
            current_user,
            page,
            per_page,
            title,
            sort_by,
            sort_order
        )
        logger.info(f"Fetched library for user {current_user.id} with media_type {media_type}")
        return response
    except ValueError as ve:
        logger.warning(f"Validation error in get_library: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in get_library: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
