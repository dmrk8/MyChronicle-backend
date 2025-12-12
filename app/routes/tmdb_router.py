from datetime import datetime, timedelta
import logging
import traceback
from typing import Optional
from fastapi import APIRouter, Path, Query, HTTPException, Depends

from app.services.tmdb_service import TMDBService
from app.core.dependencies import get_tmdb_service

tmdb_router = APIRouter(prefix="/tmdb")

logger = logging.getLogger(__name__)


@tmdb_router.get("/search/movie")
async def search_tmdb_movie(
    search: str = Query(None, min_length=1, description="search query"),
    page: int = Query(1, ge=1, description="Page number"),
    language: str = Query("en-US", description="Language for results"),
    sort_by: str = Query("popularity.desc", description="Sort by", alias="sortBy"),
    primary_release_date_gte: Optional[str] = Query(
        None,
        description="Primary release date greater than or equal to",
        alias="primaryReleaseDateGte",
    ),
    primary_release_date_lte: Optional[str] = Query(
        None,
        description="Primary release date less than or equal to",
        alias="primaryReleaseDateLte",
    ),
    with_genres: Optional[str] = Query(
        None, description="Genre IDs (comma-separated)", alias="withGenres"
    ),
    with_keywords: Optional[str] = Query(
        None, description="Keyword IDs (comma-separated)", alias="withKeywords"
    ),
    with_runtime_gte: Optional[int] = Query(
        None, ge=0, description="Minimum runtime in minutes", alias="withRuntimeGte"
    ),
    with_runtime_lte: Optional[int] = Query(
        None, ge=0, description="Maximum runtime in minutes", alias="withRuntimeLte"
    ),
    with_original_language: Optional[str] = Query(
        None, description="Original language (e.g., 'us')", alias="withOriginalLanguage"
    ),
    without_genres: Optional[str] = Query(
        None, description="Exclude genre IDs (comma-separated)", alias="withoutGenres"
    ),
    without_keywords: Optional[str] = Query(
        None, description="Exclude keyword IDs (comma-separated)", alias="withoutKeywords"
    ),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for discover movies: page={page}, language={language}, sort_by={sort_by}, "
        f"primary_release_date_gte={primary_release_date_gte}, primary_release_date_lte={primary_release_date_lte}, "
        f"with_genres={with_genres}, with_keywords={with_keywords}, with_runtime_gte={with_runtime_gte}, "
        f"with_runtime_lte={with_runtime_lte}, with_original_language={with_original_language}, "
        f"without_genres={without_genres}, without_keywords={without_keywords}"
    )
    try:
        result = await service.search_movie(
            search=search,
            page=page,
            language=language,
            sort_by=sort_by,
            primary_release_date_gte=primary_release_date_gte,
            primary_release_date_lte=primary_release_date_lte,
            with_genres=with_genres,
            with_keywords=with_keywords,
            with_runtime_gte=with_runtime_gte,
            with_runtime_lte=with_runtime_lte,
            with_original_language=with_original_language,
            without_genres=without_genres,
            without_keywords=without_keywords,
        )
        logger.info(f"Successfully returned {len(result.results)} discover movie items")
        return result
    except Exception as e:
        logger.error(f"Error fetching discover movies: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@tmdb_router.get("/search/tv")
async def search_tmdb_tv(
    search: str = Query(None, min_length=1, description="search query"),
    page: int = Query(1, ge=1, description="Page number"),
    language: str = Query("en-US", description="Language for results"),
    sort_by: str = Query("popularity.desc", description="Sort by", alias="sortBy"),
    air_date_gte: Optional[str] = Query(
        None, description="Air date greater than or equal to", alias="airDateGte"
    ),
    air_date_lte: Optional[str] = Query(
        None, description="Air date less than or equal to", alias="airDateLte"
    ),
    first_air_date_gte: Optional[str] = Query(
        None,
        description="First air date greater than or equal to",
        alias="firstAirDateGte",
    ),
    first_air_date_lte: Optional[str] = Query(
        None, description="First air date less than or equal to", alias="firstAirDateLte"
    ),
    with_genres: Optional[str] = Query(
        None, description="Genre IDs (comma-separated)", alias="withGenres"
    ),
    with_keywords: Optional[str] = Query(
        None, description="Keyword IDs (comma-separated)", alias="withKeywords"
    ),
    with_runtime_gte: Optional[int] = Query(
        None, ge=0, description="Minimum runtime in minutes", alias="withRuntimeGte"
    ),
    with_runtime_lte: Optional[int] = Query(
        None, ge=0, description="Maximum runtime in minutes", alias="withRuntimeLte"
    ),
    with_original_language: Optional[str] = Query(
        None, description="Original language (e.g., 'us')", alias="withOriginalLanguage"
    ),
    with_status: Optional[str] = Query(None, description="Status filter", alias="withStatus"),
    without_genres: Optional[str] = Query(
        None, description="Exclude genre IDs (comma-separated)", alias="withoutGenres"
    ),
    without_keywords: Optional[str] = Query(
        None, description="Exclude keyword IDs (comma-separated)", alias="withoutKeywords"
    ),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for discover TV: page={page}, language={language}, sort_by={sort_by}, "
        f"air_date_gte={air_date_gte}, air_date_lte={air_date_lte}, "
        f"first_air_date_gte={first_air_date_gte}, first_air_date_lte={first_air_date_lte}, "
        f"with_genres={with_genres}, with_keywords={with_keywords}, with_runtime_gte={with_runtime_gte}, "
        f"with_runtime_lte={with_runtime_lte}, with_original_language={with_original_language}, "
        f"with_status={with_status}, without_genres={without_genres}, without_keywords={without_keywords}"
    )
    try:
        result = await service.search_tv(
            search=search,
            page=page,
            language=language,
            sort_by=sort_by,
            air_date_gte=air_date_gte,
            air_date_lte=air_date_lte,
            first_air_date_gte=first_air_date_gte,
            first_air_date_lte=first_air_date_lte,
            with_genres=with_genres,
            with_keywords=with_keywords,
            with_runtime_gte=with_runtime_gte,
            with_runtime_lte=with_runtime_lte,
            with_original_language=with_original_language,
            with_status=with_status,
            without_genres=without_genres,
            without_keywords=without_keywords,
        )
        logger.info(f"Successfully returned {len(result.results)} discover TV items")
        return result
    except Exception as e:
        logger.error(f"Error fetching discover TV: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@tmdb_router.get("/media/movie/{movie_id}")
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


@tmdb_router.get("/media/tv/{tv_id}")
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


@tmdb_router.get("/collection/{collection_id}")
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



@tmdb_router.get("/trending/{media_type}")
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


@tmdb_router.get("/popular-season/{media_type}")
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
