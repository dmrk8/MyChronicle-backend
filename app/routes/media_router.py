from typing import List, Optional, Union
from fastapi import APIRouter, Path, Query, Depends

from app.enums.tmdb_enums import TmdbMovieSortOptions, TmdbTvSortOptions
from app.models.api.media_response_models import AnimeDetailed, MangaDetailed, MediaPagination
from app.enums.anilist_enums import AnilistSortOption, AnilistMediaType
from app.services.media_service import MediaService
from app.core.dependencies import get_media_service

media_router = APIRouter(prefix="/media")


@media_router.get("/ani/search/{media_type}", response_model=MediaPagination)
async def search_anime_manga(
    media_type: str = Path(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50, alias="perPage"),
    search: Optional[str] = Query(None, min_length=1),
    sort: AnilistSortOption = Query(AnilistSortOption.POPULARITY_DESC),
    season: Optional[str] = Query(None, pattern="^(SPRING|SUMMER|FALL|WINTER)$"),
    season_year: Optional[int] = Query(None, alias="seasonYear"),
    format: Optional[str] = Query(
        None, pattern="^(TV|TV_SHORT|MOVIE|SPECIAL|OVA|ONA|MUSIC|MANGA|NOVEL|ONE_SHOT)$"
    ),
    status: Optional[str] = Query(None),
    genre_in: Optional[List[str]] = Query(None, alias="genreIn"),
    tag_in: Optional[List[str]] = Query(None, alias="tagIn"),
    is_adult: Optional[bool] = Query(False, alias="isAdult"),
    country_of_origin: Optional[str] = Query(
        None, pattern="^(JP|KR|CN)$", alias="countryOfOrigin"
    ),
    genre_not_in: Optional[List[str]] = Query(None, alias="genreNotIn"),
    tag_not_in: Optional[List[str]] = Query(None, alias="tagNotIn"),
    service: MediaService = Depends(get_media_service),
):
    media_type_enum = AnilistMediaType(media_type.upper())
    return await service.search_anime_manga(
        page,
        per_page,
        media_type_enum,
        sort,
        search,
        season,
        season_year,
        format,
        status,
        genre_in,
        tag_in,
        is_adult,
        country_of_origin,
        genre_not_in,
        tag_not_in,
    )


@media_router.get(
    "/anime/{media_id}",
    response_model=Union[AnimeDetailed, MangaDetailed],
)
async def get_anime_detail(
    media_id: int = Path(..., ge=1, description="Media ID"),
    service: MediaService = Depends(get_media_service),
):
    return await service.get_anime_or_manga_media_detail(media_id, AnilistMediaType.ANIME)

@media_router.get("/manga/{media_id}")
async def get_manga_detail(
    media_id: int = Path(..., ge=1, description="Media ID"),
    service: MediaService = Depends(get_media_service),
):
    return await service.get_anime_or_manga_media_detail(media_id, AnilistMediaType.MANGA)

@media_router.get("/search/movie")
async def search_movie(
    search: str = Query(None, min_length=1, description="search query"),
    page: int = Query(1, ge=1, description="Page number"),
    language: str = Query("en-US", description="Language for results"),
    sort_by: TmdbMovieSortOptions = Query(
        TmdbMovieSortOptions.POPULARITY_DESC, description="Sort by", alias="sortBy"
    ),
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
        None,
        description="Exclude keyword IDs (comma-separated)",
        alias="withoutKeywords",
    ),
    service: MediaService = Depends(get_media_service),
):
    return await service.search_movie(
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


@media_router.get("/search/tv")
async def search_tv(
    search: str = Query(None, min_length=1, description="search query"),
    page: int = Query(1, ge=1, description="Page number"),
    language: str = Query("en-US", description="Language for results"),
    sort_by: TmdbTvSortOptions = Query(
        TmdbTvSortOptions.POPULARITY_DESC, description="Sort by", alias="sortBy"
    ),
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
        None,
        description="First air date less than or equal to",
        alias="firstAirDateLte",
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
    with_status: Optional[str] = Query(
        None, description="Status filter", alias="withStatus"
    ),
    without_genres: Optional[str] = Query(
        None, description="Exclude genre IDs (comma-separated)", alias="withoutGenres"
    ),
    without_keywords: Optional[str] = Query(
        None,
        description="Exclude keyword IDs (comma-separated)",
        alias="withoutKeywords",
    ),
    service: MediaService = Depends(get_media_service),
):
    return await service.search_tv(
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


@media_router.get("/movie/{movie_id}")
async def get_movie_detail(
    movie_id: int = Path(..., ge=1, description="Movie ID"),
    language: str = Query("en-US", description="Language for results"),
    service: MediaService = Depends(get_media_service),
):
    return await service.get_movie_detail(
        movie_id=movie_id,
        language=language,
    )


@media_router.get("/tv/{tv_id}")
async def get_tv_detail(
    tv_id: int = Path(..., ge=1, description="TV Show ID"),
    language: str = Query("en-US", description="Language for results"),
    service: MediaService = Depends(get_media_service),
):
    return await service.get_tv_detail(
        tv_id=tv_id,
        language=language,
    )


@media_router.get("/movie/collection/{collection_id}")
async def get_movie_collection_detail(
    collection_id: int = Path(..., ge=1, description="Collection ID"),
    language: str = Query("en-US", description="Language for results"),
    service: MediaService = Depends(get_media_service),
):
    return await service.get_movie_collection_detail(
        collection_id=collection_id,
        language=language,
    )


@media_router.get("/trending/{media_type}")
async def get_trending_movie_or_tv(
    media_type: str = Path(
        ..., pattern="^(movie|tv)$", description="Media type: movie or tv"
    ),
    time_window: str = Query(
        "week", pattern="^(day|week)$", description="Time window: day or week"
    ),
    language: str = Query("en-US", description="Language for results"),
    page: int = Query(1, ge=1, description="Page number"),
    service: MediaService = Depends(get_media_service),
):
    return await service.get_trending_movie_or_tv(
        media_type, time_window, language, page
    )


@media_router.get("/keyword/search")
async def search_keyword(
    query: str = Query(..., min_length=1, description="Keyword search query"),
    service: MediaService = Depends(get_media_service),
):
    return await service.search_keyword_for_movie_or_tv(query=query)


@media_router.get("/detail/by-internal-id/{media_id}")
async def get_media_detail_with_internal_id(
    media_id: str = Path(..., description="Internal media ID"),
    service: MediaService = Depends(get_media_service),
):
    return await service.get_media_detail_with_internal_id(media_id=media_id)


@media_router.get("/minimal/by-internal-id/{media_id}")
async def get_media_minimal_with_internal_id(
    media_id: str = Path(..., description="Internal media ID"),
    service: MediaService = Depends(get_media_service),
):
    return await service.get_media_minimal_with_internal_id(media_id=media_id)