from enum import Enum


class AnilistMediaType(str, Enum):
    ANIME = "ANIME"
    MANGA = "MANGA"


class SortOption(str, Enum):
    POPULARITY_DESC = "POPULARITY_DESC"
    POPULARITY_ASC = "POPULARITY"
    TRENDING_DESC = "TRENDING_DESC"
    TRENDING_ASC = "TRENDING"
