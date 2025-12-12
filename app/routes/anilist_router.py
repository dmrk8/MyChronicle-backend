import logging
import traceback
from typing import List, Optional
from fastapi import APIRouter, Path, Query, HTTPException, Depends
import httpx

from app.services.anilist_service import AnilistService
from app.enums.anilist_enums import SortOption
from app.core.dependencies import get_anilist_service


anilist_router = APIRouter(prefix="/anilist")

logger = logging.getLogger(__name__)


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
    logger.info(
        f"Received request for search media: "
        f"page={page}, per_page={per_page}, search={search}, "
        f"media_type={media_type}, sort={sort}, season={season}, "
        f"season_year={season_year}, format={format}, status={status}, "
        f"genre_in={genre_in}, tag_in={tag_in}, is_adult={is_adult}, "
        f"country_of_origin={country_of_origin}"
    )
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
        logger.info(f"Successfully returned {len(result.results)} search media items")
        return result
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error searching media: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code, detail=f"AniList API error: {e.response.text}"
        )
    except ValueError as e:
        logger.error(f"Validation error searching media: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error searching media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@anilist_router.get("/media/{media_id}")
async def get_media_detail(
    media_id: int = Path(..., ge=1, description="Media ID"),
    service: AnilistService = Depends(get_anilist_service),
):
    logger.info(f"Received request for media detail: media_id={media_id}")
    try:
        result = await service.get_media_detail(media_id)
        if not result:
            raise HTTPException(status_code=404, detail="Media not found")
        logger.info(f"Successfully returned media detail for ID {media_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching media detail for ID {media_id}: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
    logger.info(
        f"Received request for featured media: page={page}, per_page={per_page}, season={season}, season_year={season_year}, sort={sort}, media_type={media_type}"
    )
    try:
        result = await service.get_featured_media(
            page, per_page, season, season_year, sort, media_type
        )
        logger.info(f"Successfully returned {len(result)} featured media items")
        return result
    except Exception as e:
        logger.error(f"Error fetching featured media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")