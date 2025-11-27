from datetime import datetime, timedelta
import logging
import traceback
from typing import List, Optional
from fastapi import APIRouter, Path, Query, HTTPException, Depends
import httpx

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService
from app.enums.anilist_enums import MediaType, SortOption

search_router = APIRouter(prefix="/search")

logger = logging.getLogger(__name__)


def get_anilist_service():
    return AnilistService()


def get_tmdb_service():
    return TMDBService()

    # @search_router.get("/movie")
    # async def search_movie(
    tmdb_service: TMDBService = (Depends(get_tmdb_service),)
    query: str = (Query(min_length=1),)
    page: int = (Query(1, ge=1),)
    language: str = (Query("en-US"),)
    include_adult: bool = (Query(False),)


# ):
#   try:
#       result = await tmdb_service.search_movies(
#          query=query, page=page, language=language, include_adult=include_adult
#     )
#    if result is None:
#       raise HTTPException(status_code=500, detail="Failed to search movies")
#  return result
#    except Exception as e:
#       logger.error("Error searching movie: %s\n%s", str(e), traceback.format_exc())
#      raise HTTPException(status_code=500, detail=f"Error searching movie: {str(e)}")


@search_router.get("/anilist/{media_type}")
async def search_anilist(
    media_type: str = Path(..., regex="^(anime|manga)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50, alias="perPage"),
    search: Optional[str] = Query(None, min_length=1),
    sort: str = Query(SortOption.POPULARITY_DESC),
    season: Optional[str] = Query(None, regex="^(SPRING|SUMMER|FALL|WINTER)$"),
    season_year: Optional[int] = Query(None, alias="seasonYear"),
    format: Optional[str] = Query(
        None, regex="^(TV|TV_SHORT|MOVIE|SPECIAL|OVA|ONA|MUSIC|MANGA|NOVEL|ONE_SHOT)$"
    ),
    status: Optional[str] = Query(None),
    genre_in: Optional[List[str]] = Query(None, alias="genreIn"),
    tag_in: Optional[List[str]] = Query(None, alias="tagIn"),
    is_adult: Optional[bool] = Query(None, alias="isAdult"),
    country_of_origin: Optional[str] = Query(None, regex="^(JP|KR|CN)$", alias="countryOfOrigin"),
    service: AnilistService = Depends(get_anilist_service),
):
    logger.info(
        f"Received request for search media: "
        f"page={page}, per_page={per_page}, search={search}, "
        f"media_type={media_type}, sort={sort}, season={season}, "
        f"season_year={season_year}, format={format}, status={status}, "
        f"genre_in={genre_in}, tag_in={tag_in}, is_adult={is_adult}, "
        f"country_of_origin={country_of_origin}"
    )
    try:
        result = await service.search_media(
            page,
            per_page,
            search,
            media_type.upper(),
            sort,
            season,
            season_year,
            format,
            status,
            genre_in,
            tag_in,
            is_adult,
            country_of_origin,
        )
        logger.info(f"Successfully returned {len(result.results)} search media items")
        return result
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error searching media: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code, detail=f"AniList API error: {e.response.text}"
        )
    except ValueError as e:
        logger.error(f"Validation error searching media: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error searching media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@search_router.get("/tmdb/{media_type}")
async def search_tmdb(
    media_type: str = Path(..., regex="^(movie|tv)$", description="Media type: movie or tv"),
    start_date: Optional[str] = Query(
        None,
        description="Start date (default: 3 months ago)",
        alias="startDate"
    ),
    end_date: str = Query(
        datetime.now().strftime("%Y-%m-%d"), description="End date (default: today)",
        alias="endDate"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    language: str = Query("en-US", description="Language for results"),
    sort_by: str = Query("popularity.desc", description="Sort by", alias="sortBy"),
    with_genres: Optional[str] = Query(
        None, description="Genre IDs (comma-separated)", alias="withGenres"
    ),  # can be a comma (AND) or pipe (OR) separated query
    with_keywords: Optional[str] = Query(None, description="Keyword IDs (comma-separated)", alias="withKeywords"),
    with_runtime_gte: Optional[int] = Query(None, ge=0, description="Minimum runtime in minutes", alias="withRuntimeGte"),
    with_runtime_lte: Optional[int] = Query(None, ge=0, description="Maximum runtime in minutes", alias="withRuntimeLte"),
    with_original_language: Optional[str] = Query(
        None, description="Original language (e.g., 'us')", alias="withOriginalLanguage"
    ),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for discover media: media_type={media_type}, start_date={start_date}, end_date={end_date}, page={page}, language={language}, sort_by={sort_by}, with_genres={with_genres}, with_keywords={with_keywords}, with_runtime_gte={with_runtime_gte}, with_runtime_lte={with_runtime_lte}, with_original_language={with_original_language}"
    )
    try:
        result = await service.get_discover_media(
            media_type,
            start_date,
            end_date,
            page,
            language,
            sort_by,
            with_genres,
            with_keywords,
            with_runtime_gte,
            with_runtime_lte,
            with_original_language,
        )
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to fetch discover media")
        logger.info(f"Successfully returned {len(result.results)} discover media items")
        return result
    except Exception as e:
        logger.error(f"Error fetching discover media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
