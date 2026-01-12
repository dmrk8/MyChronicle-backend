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


class UserMediaEntrySortFields(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    TITLE = "title"
    RATING = "rating"


class UserMediaEntrySortOptions(int, Enum):
    CREATED_AT_ASC = 1
    CREATED_AT_DESC = -1
    UPDATED_AT_ASC = 1
    UPDATED_AT_DESC = -1
    TITLE_ASC = 1
    TITLE_DESC = -1
    RATING_ASC = 1
    RATING_DESC = -1


