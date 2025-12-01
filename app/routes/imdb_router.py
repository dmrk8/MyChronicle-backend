import logging
from fastapi import APIRouter, Path, HTTPException, Depends
from app.services.imdb_service import IMDBService

imdb_router = APIRouter(prefix="/imdb")

logger = logging.getLogger(__name__)


def get_imdb_service():
    return IMDBService()


@imdb_router.get("/rating/{imdb_id}")
async def get_imdb_rating(
    imdb_id: str = Path(..., description="IMDB ID (e.g., tt0111161)"),
    service: IMDBService = Depends(get_imdb_service),
):
    """
    Get IMDB aggregate rating for a given IMDB ID.
    """
    logger.info(f"Received request for IMDB rating: imdb_id={imdb_id}")
    try:
        result = await service.get_imdb_rating(imdb_id)
        logger.info(f"Successfully returned IMDB rating for {imdb_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching IMDB rating for {imdb_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
