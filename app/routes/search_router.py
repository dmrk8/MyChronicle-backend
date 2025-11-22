import logging
import traceback
from fastapi import APIRouter, Query, HTTPException, Depends

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService

search_router = APIRouter(prefix="/media/search")

logger = logging.getLogger(__name__)

def get_anilist_service():
    return AnilistService()

def get_tmdb_service():
    return TMDBService()

@search_router.get("/anime")
async def search_anime(
                        anilist_service: AnilistService = Depends(get_anilist_service),
                        query: str = Query(min_length=1),
                        page: int = Query(1, ge=1),
                        per_page: int = Query(10, ge=1, le=50)
                        ):
    try:
        return await anilist_service.search_anime(query, page, per_page)  
    except Exception as e:
        logger.error("Error searching anime: %s\n%s", str(e), traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error searching anime: {str(e)}")


@search_router.get("/comic")
async def search_comic(
                        anilist_service: AnilistService = Depends(get_anilist_service),
                        query: str = Query(min_length=1),
                        page: int = Query(1, ge=1),
                        per_page: int = Query(10, ge=1, le=50)
                        ):
    try:
        return await anilist_service.search_comic(query, page, per_page)
    except Exception as e:
        logger.error("Error searching comic: %s\n%s", str(e), traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error searching comic: {str(e)}")

@search_router.get("/movie")
async def search_movie(
                        tmdb_service: TMDBService = Depends(get_tmdb_service),
                        query: str = Query(min_length=1),
                        page: int = Query(1, ge=1),
                        language: str = Query("en-US"),
                        include_adult: bool = Query(False)
                        ):
    try:
        result = await tmdb_service.search_movies(query=query, page=page, language=language, include_adult=include_adult)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to search movies")
        return result
    except Exception as e:
        logger.error("Error searching movie: %s\n%s", str(e), traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error searching movie: {str(e)}")

