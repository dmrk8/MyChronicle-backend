# Cache TTLs (in seconds)
from typing import Optional

from app.enums.anilist_enums import AnilistMediaType, AnilistSortOption


ANILITS_DETAIL_TTL = 60 * 60 * 24  # 24 hours ANILIST_POPULAR_TTL = 60 * 60 * 12  # 12 hours ANILIST_POPULAR_TTL = 60 * 60 * 12  # 12 hours
ANILIST_POPULAR_TTL = 60 * 60 * 12  # 12 hours
ANILIST_TRENDING_TTL = 60 * 60 * 6  # 6 hours

SORT_TTL = {
    "TRENDING_DESC": ANILIST_TRENDING_TTL,
    "POPULARITY_DESC": ANILIST_POPULAR_TTL,
}
DEFAULT_SEARCH_TTL = ANILIST_POPULAR_TTL


def get_anilist_search_ttl(sort: str) -> int:
    return SORT_TTL.get(sort, DEFAULT_SEARCH_TTL)


def anilist_detail_key(media_type: AnilistMediaType, media_id: int) -> str:
    return f"anilist:{media_type.value}:{media_id}"


def anilist_search_key(
    page: int,
    per_page: int,
    media_type: AnilistMediaType,
    sort: AnilistSortOption,
    is_adult: bool,
    season: Optional[str] = None,
    season_year: Optional[int] = None,
    status: Optional[str] = None,
) -> str:
    """Generate cache key for search with parameters"""
    params = f"{media_type.value}:{sort.value}:page:{page}:perPage:{per_page}:isAdult:{is_adult}"

    if season:
        params += f":season:{season}"
    if season_year:
        params += f":seasonYear:{season_year}"
    if status:
        params += f":status:{status}"

    return f"anilist:search:{params}"
