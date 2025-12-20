from typing import List, Optional
from app.models.anilist_models import AnilistMediaDetailed, AnilistPagination, AnilistMediaMinimal
from app.integrations.anilistApi import AnilistApi
from app.enums.anilist_enums import AnilistMediaType, SortOption
from app.services.media_normalizer import MediaNormalizer
from app.models.media_models import MediaMinimal, MediaPagination, MediaDetailed


class AnilistService:
    def __init__(self, anilist_api: AnilistApi):
        self.anilist_api = anilist_api

    async def get_featured_media(
        self,
        page: int,
        per_page: int,
        season: Optional[str] = None,
        season_year: Optional[int] = None,
        sort: str = "POPULARITY_DESC",
        media_type: str = "ANIME",
    ) -> List[MediaMinimal]:

        res = await self.anilist_api.get_featured_media(
            page, per_page, season, season_year, sort, media_type
        )
        return MediaNormalizer.normalize_anilist_minimal(res)

    async def search_media(
        self,
        page: int,
        per_page: int,
        search: Optional[str] = None,
        media_type: str = AnilistMediaType.ANIME,
        sort: str = SortOption.POPULARITY_DESC,
        season: Optional[str] = None,
        season_year: Optional[int] = None,
        format: Optional[str] = None,
        status: Optional[str] = None,
        genre_in: Optional[List[str]] = None,
        tag_in: Optional[List[str]] = None,
        is_adult: Optional[bool] = None,
        country_of_origin: Optional[str] = None,
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
        )
        return MediaNormalizer.normalize_anilist_minimal_pagination(media_list, page_info)

    async def get_media_detail(self, media_id: int) -> MediaDetailed:

        res = await self.anilist_api.get_media_detail(media_id)
        return MediaNormalizer.normalize_anilist_detailed(res)
