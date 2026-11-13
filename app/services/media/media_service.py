from typing import List, Optional

from app.cache.anilist_cache import (
    anilist_search_key,
    get_anilist_search_ttl,
)
from app.cache.tmdb_cache import (
    get_tmdb_search_ttl,
    tmdb_search_key,
)
from app.enums.anilist_enums import AnilistMediaType, AnilistSortOption
from app.enums.tmdb_enums import TmdbMovieSortOptions, TmdbTvSortOptions
from app.models.api.media_response_models import (
    AnimeDetail,
    MangaDetail,
    MediaPagination,
    MovieDetail,
    TVDetail,
)

from app.models.cache.cache_models import CachedMediaPagination
from app.services.media.details.media_detail_service import MediaDetailService
from app.services.metadata.anilist_service import AnilistService
from app.services.redis_service import RedisService
from app.services.metadata.tmdb_service import TMDBService


class MediaService:
    def __init__(
        self,
        redis_service: RedisService,
        anilist_service: AnilistService,
        tmdb_service: TMDBService,
        media_detail_service: MediaDetailService,
    ):
        self.redis_service = redis_service
        self.anilist_service = anilist_service
        self.tmdb_service = tmdb_service
        self.media_detail_service = media_detail_service

    async def search_anime_manga(
        self,
        page: int,
        per_page: int,
        media_type: AnilistMediaType,
        sort: AnilistSortOption,
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
                media_type,
                sort,
                is_adult or False,
                season,
                season_year,
                status,
            )
            cached = await self.redis_service.get_cached(
                key=cache_key,
                endpoint=f"/media/anilist/search/{media_type}",
                service="anilist",
                cache_type="media_search",
                model=CachedMediaPagination,
            )
            if cached:
                return cached.data

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
            ttl = get_anilist_search_ttl(sort)
            await self.redis_service.set_cached(
                cache_key, CachedMediaPagination(data=res), ttl=ttl
            )

        return res

    async def get_anime_detail(self, media_id: int) -> AnimeDetail:
        return await self.media_detail_service.get_anime_detail(media_id)

    async def get_manga_detail(self, media_id: int) -> MangaDetail:
        return await self.media_detail_service.get_manga_detail(media_id)

    async def get_trending_movie_or_tv(
        self,
        media_type: str,
        time_window: str,
        language: str,
        page: int,
    ) -> MediaPagination:
        return await self.tmdb_service.get_trending_media(
            media_type=media_type,
            time_window=time_window,
            language=language,
            page=page,
        )

    async def search_movie(
        self,
        search: Optional[str],
        page: int,
        language: str,
        sort_by: TmdbMovieSortOptions,
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

        should_cache = (
            not search
            and not primary_release_date_gte
            and not primary_release_date_lte
            and not with_genres
            and not with_keywords
            and not with_runtime_gte
            and not with_runtime_lte
            and not with_original_language
            and not without_genres
            and not without_keywords
            and sort_by == TmdbMovieSortOptions.POPULARITY_DESC
        )
        cache_key = None
        if should_cache:
            cache_key = tmdb_search_key(
                page=page,
                media_type="movie",
                sort=sort_by,
            )
            cached = await self.redis_service.get_cached(
                key=cache_key,
                endpoint="/media/tmdb/search/movie",
                service="tmdb",
                cache_type="media_search",
                model=CachedMediaPagination,
            )
            if cached:
                return cached.data

        res = await self.tmdb_service.search_movie(
            search=search,
            page=page,
            language=language,
            sort_by=sort_by.value,
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
        if should_cache and cache_key:
            ttl = get_tmdb_search_ttl(sort_by)
            await self.redis_service.set_cached(
                cache_key, CachedMediaPagination(data=res), ttl=ttl
            )
        return res

    async def search_tv(
        self,
        search: Optional[str],
        page: int,
        language: str,
        sort_by: TmdbTvSortOptions,
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
        should_cache = (
            not search
            and not air_date_gte
            and not air_date_lte
            and not first_air_date_gte
            and not first_air_date_lte
            and not with_genres
            and not with_keywords
            and not with_runtime_gte
            and not with_runtime_lte
            and not with_original_language
            and not with_status
            and not without_genres
            and not without_keywords
            and sort_by == TmdbTvSortOptions.POPULARITY_DESC
        )
        cache_key = None
        if should_cache:
            cache_key = tmdb_search_key(
                page=page,
                media_type="tv",
                sort=sort_by,
            )
            cached = await self.redis_service.get_cached(
                key=cache_key,
                endpoint="/media/tmdb/search/tv",
                service="tmdb",
                cache_type="media_search",
                model=CachedMediaPagination,
            )
            if cached:
                return cached.data

        res = await self.tmdb_service.search_tv(
            search=search,
            page=page,
            language=language,
            sort_by=sort_by.value,
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
        if should_cache and cache_key:
            ttl = get_tmdb_search_ttl(sort_by)
            await self.redis_service.set_cached(
                cache_key, CachedMediaPagination(data=res), ttl=ttl
            )
        return res

    async def get_movie_detail(self, media_id: int) -> MovieDetail:
        return await self.media_detail_service.get_movie_detail(media_id)

    async def get_tv_detail(self, media_id: int) -> TVDetail:
        return await self.media_detail_service.get_tv_detail(media_id)

    async def search_keyword_for_movie_or_tv(
        self,
        query: str,
    ) -> List[dict]:
        return await self.tmdb_service.search_keyword(query=query)
