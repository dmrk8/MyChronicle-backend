# Cache TTLs (in seconds)
from app.enums.tmdb_enums import TmdbMovieSortOptions, TmdbTvSortOptions


TMDB_DETAIL_TTL = 60 * 60 * 24  # 24 hours
TMDB_POPULAR_TTL = 60 * 60 * 12  # 12 hours
TMDB_TRENDING_TTL = 60 * 60 * 6  # 6 hours

SORT_TTL = {
    "popularity.desc": TMDB_TRENDING_TTL,
}
DEFAULT_SEARCH_TTL = TMDB_POPULAR_TTL


def get_tmdb_search_ttl(sort: TmdbMovieSortOptions | TmdbTvSortOptions) -> int:
    return SORT_TTL.get(sort, DEFAULT_SEARCH_TTL)


def tmdb_detail_key(media_type: str, media_id: int) -> str:
    return f"tmdb:{media_type}:{media_id}"


def tmdb_search_key(
    page: int,
    media_type: str,
    sort: TmdbTvSortOptions | TmdbMovieSortOptions,
) -> str:
    """Generate cache key for search with parameters"""
    params = f"{media_type}:{sort}:page:{page}:perPage:20"

    return f"tmdb:search:{params}"
