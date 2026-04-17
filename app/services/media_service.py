from typing import List, Optional, Union

import structlog
from app.cache.anilist_cache import (
    DETAIL_TTL,
    anilist_detail_key,
    anilist_search_key,
    get_serach_ttl,
)
from app.enums.anilist_enums import AnilistMediaType
from app.models.cache.cache_models import (
    CachedAnimeDetail,
    CachedMangaDetail,
    CachedMediaPagination,
)
from app.models.media_models import (
    AnimeDetailed,
    MangaDetailed,
    MediaPagination,
    MovieCollection,
    MovieDetailed,
    TVDetailed,
)
from app.services.anilist_service import AnilistService
from app.services.redis_service import RedisService
from app.services.tmdb_service import TMDBService


logger = structlog.get_logger()


class MediaService:
    def __init__(
        self,
        redis_service: RedisService,
        anilist_service: AnilistService,
        tmdb_service: TMDBService,
    ):
        self.redis_service = redis_service
        self.anilist_service = anilist_service
        self.tmdb_service = tmdb_service

    async def search_media_anilist(
        self,
        page: int,
        per_page: int,
        media_type: AnilistMediaType,
        sort: str,
        search: Optional[str],
        season: Optional[str],
        season_year: Optional[int],
        format: Optional[str],
        status: Optional[str],
        genre_in: Optional[List[str]],
        tag_in: Optional[List[str]],
        is_adult: Optional[bool],
        country_of_origin: Optional[str],
        genre_not_in: Optional[List[str]],
        tag_not_in: Optional[List[str]],
    ) -> MediaPagination:

        cacheable_statuses = {"RELEASING", "NOT_YET_RELEASED"}
        should_cache = not any(
            [
                search,
                format,
                genre_in,
                tag_in,
                country_of_origin,
                genre_not_in,
                tag_not_in,
            ]
        )
        should_cache = should_cache and (status is None or status in cacheable_statuses)

        cache_key = None
        if should_cache:
            cache_key = anilist_search_key(
                page,
                per_page,
                media_type.value,
                sort,
                is_adult or False,
                season,
                season_year,
                status,
            )
            cached = await self.redis_service.get_cached(
                cache_key, CachedMediaPagination
            )
            if cached:
                logger.info("cache_hit", key=cache_key)
                return cached.data

            logger.info("cache_miss", key=cache_key)
        else:
            logger.debug("skipping_cache", reason="advanced_filters_provided")

        res = await self.anilist_service.search_media(
            page,
            per_page,
            media_type,
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

        # Only cache if no advanced filters
        if should_cache and cache_key:
            ttl = get_serach_ttl(sort)
            await self.redis_service.set_cached(
                cache_key, CachedMediaPagination(data=res), ttl=ttl
            )

        return res

    async def get_media_detail_anilist(
        self, media_id: int, media_type: AnilistMediaType
    ) -> Union[AnimeDetailed, MangaDetailed]:
        key = anilist_detail_key(media_type.value, media_id)
        if media_type == AnilistMediaType.ANIME:
            cached = await self.redis_service.get_cached(key, CachedAnimeDetail)
            if cached:
                logger.info("cache_hit", key=key)
                return cached.data
        else:
            cached = await self.redis_service.get_cached(key, CachedMangaDetail)
            if cached:
                logger.info("cache_hit", key=key)
                return cached.data

        logger.info("cache_miss", key=key)
        res = await self.anilist_service.get_media_detail(media_id, media_type)

        if isinstance(res, AnimeDetailed):
            await self.redis_service.set_cached(
                key, CachedAnimeDetail(data=res), ttl=DETAIL_TTL
            )
            return res
        else:
            await self.redis_service.set_cached(
                key, CachedMangaDetail(data=res), ttl=DETAIL_TTL
            )
            return res

    async def get_trending_media_tmdb(
        self, media_type: str, time_window: str, language: str, page: int
    ) -> MediaPagination:
        return await self.tmdb_service.get_trending_media(
            media_type=media_type, time_window=time_window, language=language, page=page
        )

    async def search_movie_tmdb(
        self,
        search: Optional[str],
        page: int,
        language: str,
        sort_by: str,
        primary_release_date_gte: Optional[str] = None,
        primary_release_date_lte: Optional[str] = None,
        with_genres: Optional[str] = None,
        with_keywords: Optional[str] = None,
        with_runtime_gte: Optional[int] = None,
        with_runtime_lte: Optional[int] = None,
        with_original_language: Optional[str] = None,
        without_genres: Optional[str] = None,
        without_keywords: Optional[str] = None,
    ) -> MediaPagination:

        return await self.tmdb_service.search_movie(
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

    async def search_tv_tmdb(
        self,
        search: Optional[str],
        page: int,
        language: str,
        sort_by: str,
        air_date_gte: Optional[str] = None,
        air_date_lte: Optional[str] = None,
        first_air_date_gte: Optional[str] = None,
        first_air_date_lte: Optional[str] = None,
        with_genres: Optional[str] = None,
        with_keywords: Optional[str] = None,
        with_runtime_gte: Optional[int] = None,
        with_runtime_lte: Optional[int] = None,
        with_original_language: Optional[str] = None,
        with_status: Optional[str] = None,
        without_genres: Optional[str] = None,
        without_keywords: Optional[str] = None,
    ) -> MediaPagination:
        return await self.tmdb_service.search_tv(
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

    async def get_movie_detail_tmdb(
        self,
        movie_id: int,
        language: str,
    ) -> MovieDetailed:
        return await self.tmdb_service.get_movie_detail(movie_id, language)

    async def get_tv_detail_tmdb(
        self,
        tv_id: int,
        language: str,
    ) -> TVDetailed:
        return await self.tmdb_service.get_tv_detail(tv_id, language)

    async def get_collection_detail_tmdb(
        self,
        collection_id: int,
        language: str,
    ) -> Optional[MovieCollection]:
        return await self.tmdb_service.get_collection_detail(collection_id, language)

    async def search_keyword_tmdb(
        self,
        query: str,
    ) -> List[dict]:
        return await self.tmdb_service.search_keyword(query=query)
