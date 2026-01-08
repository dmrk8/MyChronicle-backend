from fastapi import APIRouter, HTTPException, Depends, Path, Query, Body
from typing import Optional

from app.models.user_media_entry_models import (
    UserMediaEntryCreate,
    UserMediaEntryUpdate,
    UserMediaEntryPagination,
)
from app.models.user_models import UserDB

from app.services.user_media_entry_service import UserMediaEntryService
from app.core.dependencies import get_user_media_entry_service
from app.auth.auth_dependencies import get_current_user

user_media_entry_router = APIRouter(prefix="/user-media-entry", tags=["UserMediaEntry"])


@user_media_entry_router.post("/")
async def create_user_media_entry(
    entry: UserMediaEntryCreate = Body(...),
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    try:
        return await service.create_entry(entry, user.id)  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_media_entry_router.get("/{entry_id}")
async def get_user_media_entry_by_id(
    entry_id: str = Path(..., description="User Media Entry ID"),
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    try:
        return await service.get_entry_by_id(entry_id, user.id)  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@user_media_entry_router.patch("/{entry_id}")
async def update_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    update: UserMediaEntryUpdate = Body(...),
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    try:
        return await service.update_entry(entry_id, update, user.id)  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_media_entry_router.delete("/{entry_id}")
async def delete_user_media_entry(
    entry_id: str = Path(..., description="User Media Entry ID"),
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    try:
        return await service.delete_entry(entry_id, user.id)  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_media_entry_router.get("/by-user/")
async def get_entries_by_user_id(
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    try:
        return await service.get_entries_by_user_id(user.id) # type: ignore
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_media_entry_router.get("/by-external/{external_id}")
async def get_entry_by_external_id(
    external_id: int = Path(..., description="External ID"),
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    try:
        return await service.get_entry_by_external_id(external_id, user.id)  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_media_entry_router.get("/", response_model=UserMediaEntryPagination)
async def get_user_media_entries(
    page: int = Query(1, ge=1, alias="page", description="Page number"),
    per_page: int = Query(20, ge=1, le=100, alias="perPage", description="Items per page"),
    sort_by: str = Query("created_at", alias="sortBy", description="Sort by field"),
    sort_order: int = Query(
        -1, alias="sortOrder", description="Sort order: 1 for ascending, -1 for descending"
    ),
    in_library: Optional[bool] = Query(None, alias="inLibrary", description="Filter by inLibrary"),
    is_favorite: Optional[bool] = Query(None, alias="isFavorite", description="Filter by isFavorite"),
    status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    media_type: Optional[str] = Query(None, alias="mediaType", description="Filter by media type"),
    user: UserDB = Depends(get_current_user),
    service: UserMediaEntryService = Depends(get_user_media_entry_service),
):
    try:
        return await service.get_entries(
            user_id=user.id,  # type: ignore
            in_library=in_library,
            is_favorite=is_favorite,
            status=status,
            media_type=media_type,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
