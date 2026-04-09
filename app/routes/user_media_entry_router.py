from fastapi import APIRouter, Depends, Path, Query, Body
from typing import Optional

from app.models.review_models import Review, ReviewCreate, ReviewUpdate
from app.models.user_media_entry_models import (
    UserMediaEntryCreate,
    UserMediaEntryUpdate,
    UserMediaEntryPagination,
)
from app.models.user_models import User

from app.services.user_media_entry_service import UserMediaEntryService
from app.core.dependencies import get_user_media_entry_service
from app.auth.auth_dependencies import get_current_user

from app.enums.user_media_entry_enums import (
    MediaExternalSource,
    UserMediaEntrySortFields,
    UserMediaEntrySortOptions,
)

user_media_entry_router = APIRouter(
    prefix="/user-media-entries", tags=["UserMediaEntry"]
)


@user_media_entry_router.post("/")
async def create_user_media_entry(
    entry: UserMediaEntryCreate = Body(...),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.create_entry(entry, user.id)  # type: ignore


@user_media_entry_router.patch("/{entry_id}")
async def update_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    update: UserMediaEntryUpdate = Body(...),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.update_entry(entry_id, update, user.id)  # type: ignore


@user_media_entry_router.delete("/{entry_id}")
async def delete_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.delete_entry(entry_id, user.id)


@user_media_entry_router.get("/by-external/{external_source}/{external_id}")
async def get_entry_by_external_id(
    external_id: int = Path(..., description="External ID"),
    external_source: MediaExternalSource = Path(..., description="External Source"),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.get_entry_by_external_id_and_source(
        external_id, external_source, user.id
    )


@user_media_entry_router.get("/{entry_id}")
async def get_user_media_entry_by_id(
    entry_id: str = Path(..., description="User Media Entry ID"),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.get_entry_by_id(entry_id, user.id)


@user_media_entry_router.get("/", response_model=UserMediaEntryPagination)
async def get_user_media_entries(
    page: int = Query(1, ge=1, alias="page", description="Page number"),
    per_page: int = Query(
        20, ge=1, le=100, alias="perPage", description="Items per page"
    ),
    sort_by: UserMediaEntrySortFields = Query(
        UserMediaEntrySortFields.CREATED_AT, alias="sortBy", description="Sort by field"
    ),
    sort_order: UserMediaEntrySortOptions = Query(
        UserMediaEntrySortOptions.CREATED_AT_DESC,
        alias="sortOrder",
        description="Sort order: 1 for ascending, -1 for descending",
    ),
    in_library: Optional[bool] = Query(
        None, alias="inLibrary", description="Filter by inLibrary"
    ),
    is_favorite: Optional[bool] = Query(
        None, alias="isFavorite", description="Filter by isFavorite"
    ),
    status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    media_type: Optional[str] = Query(
        None, alias="mediaType", description="Filter by media type"
    ),
    title_search: Optional[str] = Query(
        None, alias="titleSearch", description="Search by title"
    ),
    is_adult: Optional[bool] = Query(
        None, alias="isAdult", description="Filter by adult content"
    ),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.get_entries(
        user_id=user.id,
        in_library=in_library,
        is_favorite=is_favorite,
        status=status,
        media_type=media_type,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        title_search=title_search,
        is_adult=is_adult,
    )


@user_media_entry_router.post("/{entry_id}/reviews", response_model=Review)
async def create_review_for_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    review: ReviewCreate = Body(...),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.create_review(review, entry_id, user.id)


@user_media_entry_router.get(
    "/{entry_id}/reviews", response_model=Optional[list[Review]]
)
async def get_reviews_for_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.get_reviews_for_user_media_entry(entry_id, user.id)


@user_media_entry_router.get("/{entry_id}/reviews/count", response_model=int)
async def count_reviews_for_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.count_reviews_for_user_media_entry(entry_id, user.id)


@user_media_entry_router.get("/{entry_id}/reviews/{review_id}", response_model=Review)
async def get_review_by_id(
    entry_id: str = Path(..., description="User Media Entry ID"),
    review_id: str = Path(..., description="Review ID"),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.get_review_by_id(review_id, user.id, entry_id)


@user_media_entry_router.patch("/{entry_id}/reviews/{review_id}", response_model=Review)
async def update_review_for_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    review_id: str = Path(..., description="Review ID"),
    update: ReviewUpdate = Body(...),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.update_review(review_id, entry_id, update, user.id)


@user_media_entry_router.delete("/{entry_id}/reviews/{review_id}")
async def delete_review_for_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    review_id: str = Path(..., description="Review ID"),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.delete_review(entry_id, review_id, user.id)


@user_media_entry_router.delete("/{entry_id}/reviews")
async def delete_reviews_for_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    user: User = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.delete_reviews_for_user_media_entry(entry_id, user.id)
