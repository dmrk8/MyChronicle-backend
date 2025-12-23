from typing import List, Optional
from app.models.anilist_models import AnilistMediaDetailed, AnilistPagination, AnilistMediaMinimal
from app.integrations.anilistApi import AnilistApi
from app.enums.anilist_enums import AnilistMediaType, SortOption
from app.utils.media_normalizer import MediaNormalizer
from app.models.media_models import MediaMinimal, MediaPagination, MediaDetailed
from app.context.anilist_season_info import get_season_context


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
    ) -> List[AnilistMediaMinimal]:

        return await self.anilist_api.get_featured_media(
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
    ) -> AnilistPagination:

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
        return AnilistPagination(
            results=media_list,
            currentPage=page_info.current_page,
            perPage=per_page,
            hasNextPage=page_info.has_next_page,
            total=page_info.total,
        )
        return MediaNormalizer.normalize_anilist_minimal_pagination(media_list, page_info)

    async def get_media_detail(self, media_id: int) -> AnilistMediaDetailed:

        return await self.anilist_api.get_media_detail(media_id)
        return MediaNormalizer.normalize_anilist_detailed(res)

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
            "trending":  MediaNormalizer.normalize_anilist_minimal(res.trending),
            "popularSeason": MediaNormalizer.normalize_anilist_minimal(res.popular_season),
            "upcoming": MediaNormalizer.normalize_anilist_minimal(res.upcoming),
            "allTime": MediaNormalizer.normalize_anilist_minimal(res.all_time)
        }
