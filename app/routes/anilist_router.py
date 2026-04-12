from typing import List, Optional, Union
from fastapi import (
    APIRouter,
    Path,
    Query,
    Depends,
)

from app.models.media_models import AnimeDetailed, MangaDetailed, MediaPagination
from app.services.anilist_service import AnilistService
from app.enums.anilist_enums import SortOption, AnilistMediaType
from app.core.dependencies import get_anilist_service


anilist_router = APIRouter(prefix="/anilist")


@anilist_router.get("/search/{media_type}", response_model=MediaPagination)
async def search_anilist(
    media_type: AnilistMediaType = Path(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50, alias="perPage"),
    search: Optional[str] = Query(None, min_length=1),
    sort: str = Query(SortOption.POPULARITY_DESC),
    season: Optional[str] = Query(None, regex="^(SPRING|SUMMER|FALL|WINTER)$"),
    season_year: Optional[int] = Query(None, alias="seasonYear"),
    format: Optional[str] = Query(
        None, regex="^(TV|TV_SHORT|MOVIE|SPECIAL|OVA|ONA|MUSIC|MANGA|NOVEL|ONE_SHOT)$"
    ),
    status: Optional[str] = Query(None),
    genre_in: Optional[List[str]] = Query(None, alias="genreIn"),
    tag_in: Optional[List[str]] = Query(None, alias="tagIn"),
    is_adult: Optional[bool] = Query(False, alias="isAdult"),
    country_of_origin: Optional[str] = Query(
        None, regex="^(JP|KR|CN)$", alias="countryOfOrigin"
    ),
    genre_not_in: Optional[List[str]] = Query(None, alias="genreNotIn"),
    tag_not_in: Optional[List[str]] = Query(None, alias="tagNotIn"),
    service: AnilistService = Depends(get_anilist_service),
):
    return await service.search_media(
        page,
        per_page,
        media_type,
        sort,
        search,
        season,
        season_year,
        format,
        status,
        genre_in,
        tag_in,
        is_adult,
        country_of_origin,
        genre_not_in,
        tag_not_in,
    )


@anilist_router.get(
    "/{media_type}/{media_id}", response_model=Union[AnimeDetailed, MangaDetailed]
)
async def get_media_detail(
    media_type: AnilistMediaType = Path(..., description="Media type (ANIME or MANGA)"),
    media_id: int = Path(..., ge=1, description="Media ID"),
    service: AnilistService = Depends(get_anilist_service),
):
    return await service.get_media_detail(media_id, media_type)
