# Cache TTLs (in seconds)
from typing import Optional


DETAIL_TTL = 60 * 60 * 24  # 24 hours
POPULAR_TTL = 60 * 60 * 12  # 12 hours
TRENDING_TTL = 60 * 60 * 6  # 6 hours

SORT_TTL = {
    "TRENDING_DESC": TRENDING_TTL,
    "POPULARITY_DESC": POPULAR_TTL,
}
DEFAULT_SEARCH_TTL = POPULAR_TTL


def get_serach_ttl(sort: str) -> int:
    return SORT_TTL.get(sort, DEFAULT_SEARCH_TTL)


def anilist_detail_key(media_type: str, media_id: int) -> str:
    return f"anilist:{media_type}:{media_id}"


def anilist_search_key(
    page: int,
    per_page: int,
    media_type: str,
    sort: str,
    is_adult: bool,
    season: Optional[str] = None,
    season_year: Optional[int] = None,
    status: Optional[str] = None,
) -> str:
    """Generate cache key for search with parameters"""
    params = f"{media_type}:{sort}:page:{page}:perPage:{per_page}:isAdult:{is_adult}"

    if season:
        params += f":season:{season}"
    if season_year:
        params += f":seasonYear:{season_year}"
    if status:
        params += f":status:{status}"

    return f"anilist:search:{params}"
