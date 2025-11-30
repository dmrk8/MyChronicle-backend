from datetime import datetime, timedelta
import logging
import traceback
from typing import List, Optional
from fastapi import APIRouter, Path, Query, HTTPException, Depends
import httpx

from app.services.anilist_service import AnilistService
from app.services.tmdb_service import TMDBService
from app.enums.anilist_enums import MediaType, SortOption
from app.enums.tmdb_enums import TMDBSortOption

search_router = APIRouter(prefix="/search")

logger = logging.getLogger(__name__)


def get_anilist_service():
    return AnilistService()


def get_tmdb_service():
    return TMDBService()


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
    primary_release_date_gte: Optional[str] = Query(
        None,
        description="Primary release date greater than or equal to (for movies)",
        alias="primaryReleaseDateGte",
    ),
    primary_release_date_lte: Optional[str] = Query(
        None,
        description="Primary release date less than or equal to (for movies)",
        alias="primaryReleaseDateLte",
    ),
    air_date_gte: Optional[str] = Query(
        None, description="Air date greater than or equal to (for TV)", alias="airDateGte"
    ),
    air_date_lte: Optional[str] = Query(
        None, description="Air date less than or equal to (for TV)", alias="airDateLte"
    ),
    first_air_date_gte: Optional[str] = Query(
        None,
        description="First air date greater than or equal to (for TV)",
        alias="firstAirDateGte",
    ),
    first_air_date_lte: Optional[str] = Query(
        None, description="First air date less than or equal to (for TV)", alias="firstAirDateLte"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    language: str = Query("en-US", description="Language for results"),
    sort_by: str = Query("popularity.desc", description="Sort by", alias="sortBy"),
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
    with_status: Optional[str] = Query(
        None, description="Status filter (for TV)", alias="withStatus"
    ),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for discover media: media_type={media_type}, primary_release_date_gte={primary_release_date_gte}, primary_release_date_lte={primary_release_date_lte}, air_date_gte={air_date_gte}, air_date_lte={air_date_lte}, first_air_date_gte={first_air_date_gte}, first_air_date_lte={first_air_date_lte}, page={page}, language={language}, sort_by={sort_by}, with_genres={with_genres}, with_keywords={with_keywords}, with_runtime_gte={with_runtime_gte}, with_runtime_lte={with_runtime_lte}, with_original_language={with_original_language}, with_status={with_status}"
    )
    try:
        result = await service.get_discover_media(
            media_type=media_type,
            page=page,
            language=language,
            sort_by=sort_by,
            primary_release_date_gte=primary_release_date_gte,
            primary_release_date_lte=primary_release_date_lte,
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
        )
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to fetch discover media")
        logger.info(f"Successfully returned {len(result.results)} discover media items")
        return result
    except Exception as e:
        logger.error(f"Error fetching discover media: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@search_router.get("test/movie")
async def search_movie_test(
    page: int = Query(1, ge=1, description="Page number"),
    sort_by: str = Query(TMDBSortOption.POPULARITY_DESC, description="Sort by", alias="sortBy"),
    language: str = Query("en-US", description="Language for results"),
    search: str = Query(None, min_length=1, description="Search query"),
    genres: List[int] = Query([], description="List of genre IDs"),
    keywords: List[int] = Query([], description="List of keyword IDs"),
    length_lte: int = Query(300, ge=0, description="Maximum length in minutes", alias="lengthLte"),
    length_gte: int = Query(0, ge=0, description="Minimum length in minutes", alias="lengthGte"),
    release_date_gte: Optional[str] = Query(
        None, description="Release date greater than or equal to", alias="releaseDateGte"
    ),
    release_date_lte: Optional[str] = Query(
        None, description="Release date less than or equal to", alias="releaseDateLte"
    ),
    with_original_language: Optional[str] = Query(
        None, description="Original language", alias="withOriginalLanguage"
    ),
    service: TMDBService = Depends(get_tmdb_service),
):
    logger.info(
        f"Received request for search movie: page={page}, sort_by={sort_by}, language={language}, search={search}, genres={genres}, keywords={keywords}, length_lte={length_lte}, length_gte={length_gte}, release_date_gte={release_date_gte}, release_date_lte={release_date_lte}, with_original_language={with_original_language}"
    )
    try:
        result = await service.search_movie_test(
            page=page,
            sort_by=sort_by,
            language=language,
            search=search,
            genres=genres,
            keywords=keywords,
            length_lte=length_lte,
            length_gte=length_gte,
            release_date_gte=release_date_gte,
            release_date_lte=release_date_lte,
            with_original_language=with_original_language,
        )
        logger.info(f"Successfully returned {len(result.results)} search movie results")
        return result
    except Exception as e:
        logger.error(f"Error searching movie: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
