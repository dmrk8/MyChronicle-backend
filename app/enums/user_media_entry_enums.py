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
    IGDB = "IGDB"


class UserMediaEntryStatus(str, Enum):
    PLANNING = "PLANNING"  # Not started
    CURRENT = "CURRENT"  # In progress (reading/watching/playing)
    ON_HOLD = "ON_HOLD"  # Paused temporarily
    COMPLETED = "COMPLETED"  # Finished
    DROPPED = "DROPPED"  # Stopped midway
