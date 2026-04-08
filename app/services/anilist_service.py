from typing import List
from app.integrations.anilistApi import AnilistApi
from app.enums.anilist_enums import AnilistMediaType
from app.utils.anilist_normalizer import AnilistNormalizer
from app.models.media_models import (
    MangaDetailed,
    MediaPagination,
    AnimeDetailed,
)
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
        return AnilistNormalizer.normalize_anime_detailed(res)
        

    async def get_manga_detail(self, manga_id: int) -> MangaDetailed:
        res = await self.anilist_api.get_media_detail(manga_id)
        return AnilistNormalizer.normalize_manga_detailed(res)

