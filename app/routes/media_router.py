import logging
import traceback
from fastapi import APIRouter, Path, Query, HTTPException, Depends

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService
from app.dependencies import get_anilist_service

media_router = APIRouter(prefix="/media")

logger = logging.getLogger(__name__)


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


@media_router.get("/tmdb/movie/{movie_id}")
async def get_tmdb_movie_detail(
    movie_id: int = Path(..., ge=1, description="Movie ID"),
    language: str = Query("en-US", description="Language for results"),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(f"Received request for TMDB movie detail: movie_id={movie_id}, language={language}")
    try:
        result = await service.get_movie_detail(
            movie_id=movie_id,
            language=language,
        )
        logger.info(f"Successfully returned movie detail for {movie_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching TMDB movie detail: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@media_router.get("/tmdb/tv/{tv_id}")
async def get_tmdb_tv_detail(
    tv_id: int = Path(..., ge=1, description="TV Show ID"),
    language: str = Query("en-US", description="Language for results"),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(f"Received request for TMDB TV detail: tv_id={tv_id}, language={language}")
    try:
        result = await service.get_tv_detail(
            tv_id=tv_id,
            language=language,
        )
        logger.info(f"Successfully returned TV detail for {tv_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching TMDB TV detail: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@media_router.get("/tmdb/collection/{collection_id}")
async def get_tmdb_collection_detail(
    collection_id: int = Path(..., ge=1, description="Collection ID"),
    language: str = Query("en-US", description="Language for results"),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for TMDB collection detail: collection_id={collection_id}, language={language}")
    try:
        result = await service.get_collection_detail(
            collection_id=collection_id,
            language=language,
        )
        logger.info(f"Successfully returned collection detail for {collection_id}")
        return result
    except Exception as e:
        logger.error(
            f"Error fetching TMDB collection detail: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
