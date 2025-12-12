import logging
import traceback
from typing import List, Optional
from fastapi import APIRouter, Path, Query, HTTPException, Depends
import httpx

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService
from app.enums.anilist_enums import SortOption
from app.dependencies import get_anilist_service
from app.dependencies import get_tmdb_service


search_router = APIRouter(prefix="/search")

logger = logging.getLogger(__name__)


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


@search_router.get("/tmdb/movie")
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


@search_router.get("/tmdb/tv")
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
