import logging
import traceback
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends

from app.services.anilist_service import AnilistService

discover_router = APIRouter(prefix="/discover")

logger = logging.getLogger(__name__)

def get_anilist_service():
    return AnilistService()

@discover_router.get("/featured")
async def get_featured_media(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50, alias="perPage"),
    season: Optional[str] = None,
    season_year: Optional[int] = Query(None, alias="seasonYear"),
    sort: str = Query(None),
    media_type: str = Query(None, alias="mediaType"),
    service: AnilistService = Depends(get_anilist_service)
):
    logger.info(f"Received request for featured media: page={page}, per_page={per_page}, season={season}, season_year={season_year}, sort={sort}, media_type={media_type}")
    try:
        result = await service.get_featured_media(page, per_page, season, season_year, sort, media_type)
        logger.info(f"Successfully returned {len(result)} featured media items")
        return result
    except Exception as e:
        logger.error(f"Error fetching featured media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")





