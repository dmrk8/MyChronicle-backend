from fastapi import APIRouter, HTTPException, Depends, Path, Query

from app.models.review_models import ReviewCreate, ReviewUpdate
from app.models.user_models import UserDB
from app.services.review_service import ReviewService
from app.auth.auth_dependencies import get_current_user
from app.core.dependencies import get_review_service

review_router = APIRouter(prefix="/reviews")


@review_router.post("/")
async def create_review(
    review_request: ReviewCreate,
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    try:
        response = await review_service.create_review(review_request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@review_router.patch("/{review_id}")
async def update_review(
    update_request: ReviewUpdate,
    review_id: str = Path(..., description="ID of the review"),
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    try:
        response = await review_service.update_review(review_id, update_request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@review_router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    try:
        response = await review_service.delete_review(review_id)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@review_router.get("/{review_id}")
async def get_review_by_id(
    review_id: str = Path(..., description="ID of the review"),
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Get the review data for the current user and a specific review ID.
    """
    try:
        response = await review_service.get_review_by_id(review_id)  # type: ignore
        return response
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@review_router.get("/entry/{user_media_entry_id}")
async def get_reviews_by_user_media_entry_id(
    user_media_entry_id: str = Path(..., description="ID of the user media entry"),
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Get all reviews for a specific user media entry.
    """
    try:
        res = await review_service.get_reviews_by_user_media_entry_id(user_media_entry_id)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@review_router.get("/by-user-id")
async def get_reviews_by_user_id_and_media_id(
    media_id: str = Query(..., description="ID of the media"),
    current_user: UserDB = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Get all reviews for a specific user and media.
    """
    try:
        reviews = await review_service.get_reviews_by_user_id_and_media_id(
            current_user.id, media_id
        )
        return reviews
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
