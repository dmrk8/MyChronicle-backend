from typing import List, Optional
from app.integrations.anilistApi import AnilistApi
from app.enums.anilist_enums import AnilistMediaType
from app.utils.anilist_normalizer import AnilistNormalizer
from app.models.media_models import (
    MangaDetailed,
    MediaFeaturedBulk,
    MediaMinimal,
    MediaPagination,
    AnimeDetailed,
)
from app.context.anilist_season_info import get_season_context
import structlog

logger = structlog.get_logger("anilist_service")


class AnilistService:
    def __init__(self, anilist_api: AnilistApi):
        self.anilist_api = anilist_api

    async def search_media(
        self,
        page: int,
        per_page: int,
        search: str,
        media_type: str,
        sort: str,
        season: str,
        season_year: int,
        format: str,
        status: str,
        genre_in: List[str],
        tag_in: List[str],
        is_adult: bool,
        country_of_origin: str,
        genre_not_in: List[str],
        tag_not_in: List[str],
    ) -> MediaPagination:

        media_list, page_info = await self.anilist_api.search_media(
            page,
            per_page,
            search,
            media_type,
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
        return MediaPagination(
            results=AnilistNormalizer.normalize_minimal(media_list),
            currentPage=page_info.current_page,
            perPage=per_page,
            hasNextPage=page_info.has_next_page,
            total=page_info.total,
        )

    async def get_anime_detail(self, anime_id: int) -> AnimeDetailed:
        res = await self.anilist_api.get_media_detail(anime_id)
        if res.type != AnilistMediaType.ANIME:
            raise TypeError(f"Expected ANIME, got {res.type}")
        return AnilistNormalizer.normalize_anime_detailed(res)
        

    async def get_manga_detail(self, manga_id: int) -> MangaDetailed:
        res = await self.anilist_api.get_media_detail(manga_id)
        if res.type != AnilistMediaType.MANGA:
            raise TypeError(f"Expected MANGA, got {res.type}")
        return AnilistNormalizer.normalize_manga_detailed(res)

    async def get_featured_media_bulk(
        self,
        media_type: str,
    ):
        """
        Fetches featured media data: all time popular, trending now, popular this season, and upcoming next season.
        """
        seasont_ctx = get_season_context()

        res = await self.anilist_api.get_featured_media_bulk(
            page=1,
            per_page=6,
            media_type=media_type,
            current_season=seasont_ctx["currentSeason"],
            current_season_year=seasont_ctx["currentSeasonYear"],
            next_season=seasont_ctx["nextSeason"],
            next_season_year=seasont_ctx["nextSeasonYear"],
        )
        return {
            "trending": AnilistNormalizer.normalize_minimal(res.trending),
            "popularSeason": AnilistNormalizer.normalize_minimal(res.popular_season),
            "upcoming": AnilistNormalizer.normalize_minimal(res.upcoming),
            "allTime": AnilistNormalizer.normalize_minimal(res.all_time),
        }

    async def get_featured_manga_bulk(
        self,
        media_type: str,
        page: int,
        per_page: int,
    ):
        """
        Fetches featured manga data: trending, all time popular, and all time popular Manhwa.
        """
        res = await self.anilist_api.get_featured_manga_bulk(
            page=page,
            per_page=per_page,
            media_type=media_type,
        )
        return {
            "trending": AnilistNormalizer.normalize_minimal(res["trending"]),
            "allTime": AnilistNormalizer.normalize_minimal(res["allTime"]),
            "allTimeManhwa": AnilistNormalizer.normalize_minimal(res["allTimeManhwa"]),
        }

    async def get_featured_bulk(
        self,
        media_type: str,
        page: int,
        per_page: int,
    ) -> MediaFeaturedBulk:
        """
        Fetches featured anime and/or manga data in bulk.
        """
        if media_type == "ANIME":
            season_ctx = get_season_context()
            anime_res = await self.anilist_api.get_featured_media_bulk(
                page=page,
                per_page=per_page,
                media_type=media_type,
                current_season=season_ctx["currentSeason"],
                current_season_year=season_ctx["currentSeasonYear"],
                next_season=season_ctx["nextSeason"],
                next_season_year=season_ctx["nextSeasonYear"],
            )
            return MediaFeaturedBulk(
                trending=AnilistNormalizer.normalize_minimal(anime_res.trending),
                popularSeason=AnilistNormalizer.normalize_minimal(
                    anime_res.popular_season
                ),
                upcoming=AnilistNormalizer.normalize_minimal(anime_res.upcoming),
                all_time=AnilistNormalizer.normalize_minimal(anime_res.all_time),  # type: ignore
            )
        else:
            res = await self.anilist_api.get_featured_manga_bulk(
                page=page,
                per_page=per_page,
                media_type=media_type,
            )
            return MediaFeaturedBulk(
                trending=AnilistNormalizer.normalize_minimal(res.trending),  # type: ignore
                allTime=AnilistNormalizer.normalize_minimal(res.all_time),  # type: ignore
                allTimeManhwa=AnilistNormalizer.normalize_minimal(res.all_time_manhwa),  # type: ignore
            )
