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
    
class AnilistFormat(str, Enum):
    TV = "TV"
    TV_SHORT = "TV_SHORT"
    MOVIE = "MOVIE"
    SPECIAL = "SPECIAL"
    OVA = "OVA"
    ONA = "ONA"
    MUSIC = "MUSIC"
    MANGA = "MANGA"
    NOVEL = "NOVEL"
    ONE_SHOT = "ONE_SHOT"
    
class AnilistSeason(str, Enum):
    WINTER = "WINTER"
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    FALL = "FALL"
    
    
class AnilistCountryOfOrigin(str, Enum):
    JAPAN = "JP"
    KOREA = "KR"
    CHINA = "CN"
    
    