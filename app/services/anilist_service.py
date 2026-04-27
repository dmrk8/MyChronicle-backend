from typing import List, Optional

from app.integrations.anilist_api import AnilistApi
from app.enums.anilist_enums import AnilistMediaType
from app.models.api.anilist_models import AnilistMediaDetailed
from app.utils.anilist_normalizer import AnilistNormalizer
from app.models.media_models import (
    MediaPagination,
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

        return result

    async def get_media_detail(
        self, media_id: int
    ) -> AnilistMediaDetailed:
        return await self.anilist_api.get_media_detail(media_id)
