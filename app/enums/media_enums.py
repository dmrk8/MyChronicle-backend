from enum import Enum


class MediaType(str, Enum):
    ANIME = "ANIME"
    MANGA = "MANGA"
    MOVIE = "MOVIE"
    TV = "TV"


class MediaExternalSource(str, Enum):
    ANILIST = "ANILIST"
    TMDB = "TMDB"
    OMDB = "OMDB"
    MAL = "MAL"


class StoredDataType(str, Enum):
    MEDIA_DETAILS = "MEDIA_DETAILS"
    OMDB_DATA = "OMDB_DATA"
    MAL_DATA = "MAL_DATA"
