import asyncio
from typing import List, Optional, Union

import structlog
from app.cache.anilist_cache import (
    ANILIST_DETAIL_TTL,
    anilist_detail_key,
    anilist_search_key,
    get_anilist_search_ttl,
)
from app.cache.tmdb_cache import (
    TMDB_DETAIL_TTL,
    get_tmdb_search_ttl,
    tmdb_detail_key,
    tmdb_search_key,
)
from app.core.exceptions import NotFoundException
from app.enums.anilist_enums import AnilistMediaType, AnilistSortOption
from app.enums.media_enums import MediaExternalSource, MediaType
from app.enums.tmdb_enums import TmdbMovieSortOptions, TmdbTvSortOptions
from app.models.api.media_response import (
    AnimeDetailed,
    MangaDetailed,
    MediaPagination,
    MovieDetailedWithCollection,
)
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBCollection, TMDBTVDetail
from app.models.cache.cache_models import (
    CachedAnimeDetail,
    CachedMangaDetail,
    CachedMediaPagination,
    CachedMovieDetailWithCollection,
    CachedTVDetail,
    CachedTVDetail,
)
from app.models.db.external_storage_models import MovieWithCollection
from app.services.anilist_service import AnilistService
from app.services.external_storage_service import ExternalStorageService
from app.services.media_core_service import MediaCoreService
from app.services.redis_service import RedisService
from app.services.media_sync_service import SyncService
from app.services.tmdb_service import TMDBService
from app.utils.normalizers.media_response_normalizer import MediaNormalizer


class MediaService:
    def __init__(
        self,
        redis_service: RedisService,
        anilist_service: AnilistService,
        tmdb_service: TMDBService,
        sync_service: SyncService,
        media_core_service: MediaCoreService,
        external_storage_service: ExternalStorageService,
    ):
        self.redis_service = redis_service
        self.anilist_service = anilist_service
        self.tmdb_service = tmdb_service
        self.sync_service = sync_service
        self.media_core_service = media_core_service
        self.external_storage_service = external_storage_service

    async def search_media_anilist(
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

    async def _get_and_normalize_anilist_media(
        self,
        media_id: int,
        media_type: MediaType,
        expected_payload_type: type,
        normalizer_func,
        cache_key: str,
        cache_model,
        cache_ttl: int,
    ) -> Union[AnimeDetailed, MangaDetailed]:
        if cache_key:
            cached = await self.redis_service.get_cached(
                key=cache_key,
                endpoint=f"/media/anilist/{media_type}/:id",
                service="anilist",
                cache_type="media_detail",
                model=cache_model,
            )
            if cached:
                return cached.data

        data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
            media_id, MediaExternalSource.ANILIST, media_type
        )
        if not data:
            await self.sync_service.sync_anilist_media(media_id, media_type)
            data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
                media_id, MediaExternalSource.ANILIST, media_type=media_type
            )
        elif data and not data.is_fresh:
            asyncio.create_task(
                self.sync_service.sync_anilist_media(media_id, media_type)
            )
        if data and isinstance(data.payload, expected_payload_type):
            res = normalizer_func(data.payload)
            if cache_key:
                await self.redis_service.set_cached(
                    cache_key, cache_model(data=res), ttl=cache_ttl
                )
            return res
        raise NotFoundException()

    async def get_media_detail_anilist(
        self, media_id: int, media_type: AnilistMediaType
    ) -> Union[AnimeDetailed, MangaDetailed]:
        key = anilist_detail_key(media_type, media_id)
        if media_type == AnilistMediaType.ANIME:
            return await self._get_and_normalize_anilist_media(
                media_id=media_id,
                media_type=MediaType.ANIME,
                expected_payload_type=AnilistMediaDetail,
                normalizer_func=MediaNormalizer.to_anime_detailed,
                cache_key=key,
                cache_model=CachedAnimeDetail,
                cache_ttl=ANILIST_DETAIL_TTL,
            )
        else:
            return await self._get_and_normalize_anilist_media(
                media_id=media_id,
                media_type=MediaType.MANGA,
                expected_payload_type=AnilistMediaDetail,
                normalizer_func=MediaNormalizer.to_manga_detailed,
                cache_key=key,
                cache_model=CachedMangaDetail,
                cache_ttl=ANILIST_DETAIL_TTL,
            )

    async def get_trending_media_tmdb(
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

    async def search_movie_tmdb(
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

    async def search_tv_tmdb(
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

    async def get_movie_detail_tmdb(
        self,
        movie_id: int,
        language: str,
    ) -> MovieDetailedWithCollection:
        cache_key = tmdb_detail_key("movie", movie_id)
        if cache_key:
            cached = await self.redis_service.get_cached(
                key=cache_key,
                endpoint="/media/tmdb/movie/:id",
                service="tmdb",
                cache_type="media_detail",
                model=CachedMovieDetailWithCollection,
            )
            if cached:
                return cached.data

        data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
            movie_id, MediaExternalSource.TMDB, MediaType.MOVIE
        )

        if not data:
            await self.sync_service.sync_tmdb_movie(movie_id, MediaType.MOVIE)
            data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
                movie_id, MediaExternalSource.TMDB, MediaType.MOVIE
            )
        elif data and not data.is_fresh:
            asyncio.create_task(
                self.sync_service.sync_tmdb_movie(movie_id, MediaType.MOVIE)
            )

        if data and isinstance(data.payload, MovieWithCollection):
            omdb_data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
                movie_id, MediaExternalSource.OMDB, MediaType.MOVIE
            )
            omdb_payload = None
            if omdb_data and isinstance(omdb_data.payload, OMDbData):
                omdb_payload = omdb_data.payload
            res = MediaNormalizer.to_movie_detailed_with_collection(
                data.payload, omdb_payload
            )
            if cache_key:
                await self.redis_service.set_cached(
                    cache_key,
                    CachedMovieDetailWithCollection(data=res),
                    ttl=TMDB_DETAIL_TTL,
                )
            return res
        raise NotFoundException()

    async def get_tv_detail_tmdb(
        self,
        tv_id: int,
        language: str,
    ):
        cache_key = tmdb_detail_key("tv", tv_id)
        if cache_key:
            cached = await self.redis_service.get_cached(
                key=cache_key,
                endpoint="/media/tmdb/tv/:id",
                service="tmdb",
                cache_type="media_detail",
                model=CachedTVDetail,
            )
            if cached:
                return cached.data
        data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
            tv_id, MediaExternalSource.TMDB, MediaType.TV
        )
        if not data:
            await self.sync_service.sync_tmdb_tv(tv_id, MediaType.TV)
            data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
                tv_id, MediaExternalSource.TMDB, MediaType.TV
            )
        elif data and not data.is_fresh:
            asyncio.create_task(self.sync_service.sync_tmdb_tv(tv_id, MediaType.TV))
        if data and isinstance(data.payload, TMDBTVDetail):
            omdb_data = await self.external_storage_service.get_by_external_id_and_source_and_media_type(
                tv_id, MediaExternalSource.OMDB, MediaType.TV
            )
            omdb_payload = None
            if omdb_data and isinstance(omdb_data.payload, OMDbData):
                omdb_payload = omdb_data.payload
            res = MediaNormalizer.to_tv_detailed(data.payload, omdb_payload)
            if cache_key:
                await self.redis_service.set_cached(
                    cache_key, CachedTVDetail(data=res), ttl=TMDB_DETAIL_TTL
                )
                return res
        raise NotFoundException()

    async def get_collection_detail_tmdb(
        self,
        collection_id: int,
        language: str,
    ) -> Optional[TMDBCollection]:
        return await self.tmdb_service.get_collection_detail(collection_id, language)

    async def search_keyword_tmdb(
        self,
        query: str,
    ) -> List[dict]:
        return await self.tmdb_service.search_keyword(query=query)
