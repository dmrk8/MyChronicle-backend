import logging
import traceback
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Path, Query, HTTPException, Depends

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService

from app.dependencies import get_tmdb_service
from app.dependencies import get_anilist_service

discover_router = APIRouter(prefix="/discover")

logger = logging.getLogger(__name__)


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


@discover_router.get("/tmdb/popular-season/{media_type}")
async def get_tmdb_popular_season(
    media_type: str = Path(..., regex="^(movie|tv)$", description="Media type: movie or tv"),
    start_date: str = Query(
        (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
        description="Start date (default: 3 months ago)",
    ),
    end_date: str = Query(
        datetime.now().strftime("%Y-%m-%d"), description="End date (default: today)"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    language: str = Query("en-US", description="Language for results"),
    sort_by: str = Query("popularity.desc", description="Sort by"),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for popular season media: media_type={media_type}, start_date={start_date}, end_date={end_date}, page={page}, language={language}, sort_by={sort_by}"
    )
    try:
        result = await service.get_popular_season(
            media_type, start_date, end_date, page, language, sort_by
        )
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to fetch popular season media")
        logger.info(f"Successfully returned {len(result.results)} popular season media items")
        return result
    except Exception as e:
        logger.error(f"Error fetching popular season media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
