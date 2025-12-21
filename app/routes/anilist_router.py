from typing import List, Optional
from fastapi import APIRouter, Path, Query, HTTPException, Depends, status as http_status
import httpx

from app.models.anilist_models import AnilistPagination
from app.services.anilist_service import AnilistService
from app.enums.anilist_enums import SortOption, AnilistMediaType
from app.core.dependencies import get_anilist_service


anilist_router = APIRouter(prefix="/anilist")


@anilist_router.get("/search/{media_type}")
async def search_anilist(
    media_type: str = Path(..., regex="^(anime|manga)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50, alias="perPage"),
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
    is_adult: Optional[bool] = Query(None, alias="isAdult"),
    country_of_origin: Optional[str] = Query(None, regex="^(JP|KR|CN)$", alias="countryOfOrigin"),
    service: AnilistService = Depends(get_anilist_service),
):
    try:
        result = await service.search_media(
            page,
            per_page,
            search,
            media_type.upper(),
            sort,
            season,
            season_year,
            format,
            status,
            genre_in,
            tag_in,
            is_adult,
            country_of_origin,
        )

        return result
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="AniList API error")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@anilist_router.get("/media/{media_id}")
async def get_media_detail(
    media_id: int = Path(..., ge=1, description="Media ID"),
    service: AnilistService = Depends(get_anilist_service),
):
    try:
        result = await service.get_media_detail(media_id)
        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail="Media not found"
            )
        return result
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="AniList API error")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@anilist_router.get("/featured")
async def get_anilist_featured_media(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50, alias="perPage"),
    season: Optional[str] = None,
    season_year: Optional[int] = Query(None, alias="seasonYear"),
    sort: str = Query(None),
    media_type: str = Query(None, alias="mediaType"),
    service: AnilistService = Depends(get_anilist_service),
):
    try:
        result = await service.get_featured_media(
            page, per_page, season, season_year, sort, media_type
        )
        return result
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="AniList API error")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@anilist_router.get("/featured/bulk")
async def get_anilist_featured_media_bulk(
    media_type: str = Query(AnilistMediaType.ANIME, alias="mediaType"),
    service: AnilistService = Depends(get_anilist_service),
):
    """
    Fetches featured media data: all time popular, trending now, popular this season, and upcoming next season.
    """
    try:
        return await service.get_featured_media_bulk(media_type)
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="AniList API error")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )
