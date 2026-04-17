from enum import Enum


class MediaType(str, Enum):
    ANIME = "ANIME"
    MANGA = "MANGA"
    GAME = "GAME"
    MOVIE = "MOVIE"
    TV = "TV"


class MediaExternalSource(str, Enum):
    ANILIST = "ANILIST"
    TMDB = "TMDB"
    OMDB = "OMDB"


class DataFreshnessStatus(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    OUTDATED = "OUTDATED"
    UNKNOWN = "UNKNOWN"


class SyncFrequency(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MANUAL = "MANUAL"


