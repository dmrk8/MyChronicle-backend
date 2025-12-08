import logging
import traceback
from fastapi import APIRouter, Path, HTTPException, Depends
from app.services.igdb_service import IGDBService

igdb_router = APIRouter(prefix="/igdb")

logger = logging.getLogger(__name__)


def get_igdb_service():
    return IGDBService()


@igdb_router.get("/game/{game_id}")
async def get_igdb_game_detail(
    game_id: int = Path(..., ge=1, description="Game ID"),
    service: IGDBService = Depends(get_igdb_service),
):
    logger.info(f"Received request for IGDB game detail: game_id={game_id}")
    try:
        result = await service.get_game_detail(game_id)
        logger.info(f"Successfully returned game detail for {game_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching IGDB game detail: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
