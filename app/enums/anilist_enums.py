from enum import Enum


class AnilistMediaType(str, Enum):
    ANIME = "ANIME"
    MANGA = "MANGA"


class AnilistSortOption(str, Enum):
    POPULARITY_DESC = "POPULARITY_DESC"
    POPULARITY_ASC = "POPULARITY"
    TRENDING_DESC = "TRENDING_DESC"
    TRENDING_ASC = "TRENDING"


class AnilistStatus(str, Enum):
    FINISHED = "FINISHED"
    RELEASING = "RELEASING"
    NOT_YET_RELEASED = "NOT_YET_RELEASED"
    CANCELLED = "CANCELLED"
    HIATUS = "HIATUS"
    
    