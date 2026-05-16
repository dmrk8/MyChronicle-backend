from fastapi import APIRouter, Depends, Path, Query, status
from typing import Optional

from app.core.dependencies import (
    get_review_service,
    get_user_media_entry_service,
)
from app.enums.media_enums import MediaType
from app.models.db.review_models import Review, ReviewCreate, ReviewUpdate
from app.models.db.user_media_entry_models import (
    UserMediaEntry,
    UserMediaEntryCreate,
    UserMediaEntrySyncMetadata,
    UserMediaEntryUpdate,
    UserMediaEntryPagination,
)
from app.models.db.user_models import UserDB

from app.services.review_service import ReviewService
from app.services.user_media_entry_service import UserMediaEntryService
from app.auth.auth_dependencies import get_current_user

from app.enums.user_media_entry_enums import (
    UserMediaEntrySortFields,
    UserMediaEntrySortOptions,
    UserMediaEntryStatus,
)

user_media_entry_router = APIRouter(
    prefix="/user-media-entries", tags=["user-media-entries"]
)


@user_media_entry_router.post(
    "/", response_model=UserMediaEntry, status_code=status.HTTP_201_CREATED
)
async def create_user_media_entry(
    entry: UserMediaEntryCreate,
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.create_entry(entry, str(user.id))


@user_media_entry_router.patch("/{entry_id}", response_model=UserMediaEntry)
async def update_user_media_entry(
    update: UserMediaEntryUpdate,
    entry_id: str,
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    res = await service.update_entry(entry_id, update, str(user.id))
    return UserMediaEntry.model_validate(res.model_dump())


@user_media_entry_router.delete("/{entry_id}", response_model=None)
async def delete_user_media_entry(
    entry_id: str,
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    return await service.delete_entry(entry_id, str(user.id))


@user_media_entry_router.get(
    "/{media_id}",
    response_model=UserMediaEntry,
)
async def get_entry_by_media_id(
    media_id: str = Path(..., description="Media ID"),
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    res = await service.get_entry_by_media_id_and_user_id(media_id, str(user.id))
    return UserMediaEntry.model_validate(res.model_dump())


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
    status: Optional[UserMediaEntryStatus] = Query(
        None, alias="status", description="Filter by status"
    ),
    media_type: Optional[MediaType] = Query(
        None, alias="mediaType", description="Filter by media type"
    ),
    title_search: Optional[str] = Query(
        None, alias="titleSearch", description="Search by title"
    ),
    is_adult: Optional[bool] = Query(
        None, alias="isAdult", description="Filter by adult content"
    ),
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    entries, page, per_page, has_next_page, total = (
        await service.get_entries_by_filters(
            user_id=str(user.id),
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
    )
    return UserMediaEntryPagination(
        results=[
            UserMediaEntry.model_validate(entry.model_dump()) for entry in entries
        ],
        page=page,
        perPage=per_page,
        hasNextPage=has_next_page,
        total=total,
    )


@user_media_entry_router.patch("/{entry_id}/metadata", response_model=UserMediaEntry)
async def sync_user_media_entry_metadata(
    metadata: UserMediaEntrySyncMetadata,
    entry_id: str,
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    """Sync metadata (title, cover_image, is_adult) from external API"""
    res = await service.sync_entry_metadata(entry_id, metadata, str(user.id))
    return UserMediaEntry.model_validate(res.model_dump())


# Review routes for a specific user media entry


@user_media_entry_router.post("/{entry_id}/reviews", response_model=Review)
async def create_review_for_user_media_entry(
    review: ReviewCreate,
    entry_id: str = Path(..., description="UserDB Media Entry ID"),
    user: UserDB = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    res = await service.create_review(review, entry_id, str(user.id))
    return Review.model_validate(res.model_dump())


@user_media_entry_router.get("/{entry_id}/reviews", response_model=list[Review])
async def get_reviews_for_user_media_entry(
    entry_id: str = Path(..., description="UserDB Media Entry ID"),
    user: UserDB = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    res = await service.get_reviews_for_user_media_entry(entry_id, str(user.id))
    return [Review.model_validate(review.model_dump()) for review in res]


@user_media_entry_router.get("/{entry_id}/reviews/count", response_model=int)
async def count_reviews_for_user_media_entry(
    entry_id: str = Path(..., description="UserDB Media Entry ID"),
    user: UserDB = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    return await service.count_reviews_for_user_media_entry(entry_id, str(user.id))


@user_media_entry_router.get("/{entry_id}/reviews/{review_id}", response_model=Review)
async def get_review_by_id(
    entry_id: str = Path(..., description="UserDB Media Entry ID"),
    review_id: str = Path(..., description="Review ID"),
    user: UserDB = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    res = await service.get_review_by_id(review_id, str(user.id), entry_id)
    return Review.model_validate(res.model_dump())


@user_media_entry_router.patch("/{entry_id}/reviews/{review_id}", response_model=Review)
async def update_review(
    update: ReviewUpdate,
    entry_id: str = Path(..., description="UserDB Media Entry ID"),
    review_id: str = Path(..., description="Review ID"),
    user: UserDB = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    res = await service.update_review(review_id, entry_id, update, str(user.id))
    return Review.model_validate(res.model_dump()) if res else None


@user_media_entry_router.delete(
    "/{entry_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_review_for_user_media_entry(
    entry_id: str = Path(..., description="UserDB Media Entry ID"),
    review_id: str = Path(..., description="Review ID"),
    user: UserDB = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    return await service.delete_review(entry_id, review_id, str(user.id))


@user_media_entry_router.delete(
    "/{entry_id}/reviews", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_reviews_for_user_media_entry(
    entry_id: str = Path(..., description="UserDB Media Entry ID"),
    user: UserDB = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    return await service.delete_reviews_for_user_media_entry(entry_id, str(user.id))
