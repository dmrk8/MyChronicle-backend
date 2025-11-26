import logging
import traceback
from typing import Optional
from fastapi import APIRouter, Path, Query, HTTPException, Depends

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService

discover_router = APIRouter(prefix="/discover")

logger = logging.getLogger(__name__)


def get_anilist_service():
    return AnilistService()


def get_tmdb_service():
    return TMDBService()


@discover_router.get("/anilist/featured")
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


@discover_router.get("/tmdb/trending/{media_type}")
async def get_tmdb_trending_media(
    media_type: str = Path(..., regex="^(movie|tv)$", description="Media type: movie or tv"),
    time_window: str = Query("week", regex="^(day|week)$", description="Time window: day or week"),
    language: str = Query("en-US", description="Language for results"),
    page: int = Query(1, ge=1, description="Page number"),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for trending media: media_type={media_type}, time_window={time_window}, language={language}, page={page}"
    )
    try:
        result = await service.get_trending_media(media_type, time_window, language, page)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to fetch trending media")
        logger.info(f"Successfully returned {len(result.results)} trending media items")
        return result
    except Exception as e:
        logger.error(f"Error fetching trending media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
