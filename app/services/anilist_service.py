from typing import List, Union, Optional
from app.cache.anilist_cache import (
    DETAIL_TTL,
    anilist_detail_key,
    anilist_search_key,
    get_serach_ttl,
)
from app.integrations.anilistApi import AnilistApi
from app.enums.anilist_enums import AnilistMediaType
from app.models.cache_models import (
    CachedAnimeDetail,
    CachedMangaDetail,
    CachedMediaPagination,
)
from app.services.redis_service import RedisService
from app.utils.anilist_normalizer import AnilistNormalizer
from app.models.media_models import (
    MangaDetailed,
    MediaPagination,
    AnimeDetailed,
)
import structlog

logger = structlog.get_logger("anilist_service")


class AnilistService:
    def __init__(self, anilist_api: AnilistApi, redis_service: RedisService):
        self.anilist_api = anilist_api
        self.redis_service = redis_service

    async def search_media(
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

        # Fetch from API
        media_list, page_info = await self.anilist_api.search_media(
            page,
            per_page,
            search,
            media_type.value,
            sort,
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

        result = MediaPagination(
            results=AnilistNormalizer.normalize_minimal(media_list),
            currentPage=page_info.current_page,
            perPage=per_page,
            hasNextPage=page_info.has_next_page,
            total=page_info.total,
        )

        # Only cache if no advanced filters
        if should_cache and cache_key:
            ttl = get_serach_ttl(sort)
            await self.redis_service.set_cached(
                cache_key, CachedMediaPagination(data=result), ttl=ttl
            )

        return result

    async def get_media_detail(
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
        res = await self.anilist_api.get_media_detail(media_id)

        if media_type == AnilistMediaType.ANIME:
            detailed = AnilistNormalizer.normalize_anime_detailed(res)
            await self.redis_service.set_cached(
                key, CachedAnimeDetail(data=detailed), ttl=DETAIL_TTL
            )
            return detailed
        else:
            detailed = AnilistNormalizer.normalize_manga_detailed(res)
            await self.redis_service.set_cached(
                key, CachedMangaDetail(data=detailed), ttl=DETAIL_TTL
            )
            return detailed
