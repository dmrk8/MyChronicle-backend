import logging
import traceback
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService

search_router = APIRouter(prefix="/search")

logger = logging.getLogger(__name__)

def get_anilist_service():
    return AnilistService()

def get_tmdb_service():
    return TMDBService()


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

@search_router.get("/anime")
async def search_media(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50, alias="perPage"),
    search: Optional[str] = Query(None),
    sort: str = Query(None),  
    season: Optional[str] = Query(None),
    season_year: Optional[int] = Query(None, alias="seasonYear"),
    format: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    genre_in: Optional[List[str]] = Query(None, alias="genreIn"),
    tag_in: Optional[List[str]] = Query(None, alias="tagIn"),
    service: AnilistService = Depends(get_anilist_service)
):
    logger.info(f"Received request for search media: page={page}, per_page={per_page}, media_type={"anime"}, sort={sort}, season={season}, season_year={season_year}, format={format}, status={status}, genre_in={genre_in}, tag_in={tag_in}")
    try:
        result = await service.search_media(page, per_page, search, "ANIME", sort, season, season_year, format, status, genre_in, tag_in)
        logger.info(f"Successfully returned {len(result.results)} search media items")
        return result
    except Exception as e:
        logger.error(f"Error searching media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
