import logging
import traceback
from fastapi import APIRouter, Path, Query, HTTPException, Depends

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService

media_router = APIRouter(prefix="/media")

logger = logging.getLogger(__name__)


def get_anilist_service():
    return AnilistService()


def get_tmdb_service():
    return TMDBService()


@media_router.get("/anilist/{media_id}")
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


@media_router.get("/tmdb/{media_type}/{media_id}")
async def get_tmdb_media_detail(
    media_type: str = Path(..., regex="^(movie|tv)$", description="Media type: movie or tv"),
    media_id: int = Path(..., ge=1, description="Media ID"),
    language: str = Query("en-US", description="Language for results"),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for TMDB media detail: media_type={media_type}, media_id={media_id}, language={language}"
    )
    try:
        result = await service.get_media_detail(
            media_type=media_type,
            media_id=media_id,
            language=language,
        )
        logger.info(f"Successfully returned media detail for {media_type} {media_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching TMDB media detail: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
