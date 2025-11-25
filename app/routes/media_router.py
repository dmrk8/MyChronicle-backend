import logging
import traceback
from fastapi import APIRouter, Path, HTTPException, Depends

from app.services.anilist_service import AnilistService

media_router = APIRouter(prefix="/media")

logger = logging.getLogger(__name__)


def get_anilist_service():
    return AnilistService()


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
