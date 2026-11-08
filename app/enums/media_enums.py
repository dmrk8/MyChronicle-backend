from enum import Enum


class MediaType(str, Enum):
    ANIME = "anime"
    MANGA = "manga"
    MOVIE = "movie"
    TV = "tv"


class MediaExternalSource(str, Enum):
    ANILIST = "anilist"
    TMDB = "tmdb"
    OMDB = "omdb"
    MAL = "mal"

class MediaStatus(str, Enum):
    UPCOMING = "upcoming"
    RELEASING = "releasing"
    FINISHED = "finished"
    HIATUS = "hiatus"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

    
class StoredDataType(str, Enum):
    ANILIST_MEDIA_DETAIL = "anilist_media_detail"
    TMDB_MOVIE_DETAIL = "tmdb_movie_detail"
    TMDB_TV_DETAIL = "tmdb_tv_detail"
    TMDB_COLLECTION = "tmdb_collection"
    OMDB_DATA = "omdb_data"
    MAL_MANGA_DATA = "mal_manga_data"
    MAL_ANIME_DATA = "mal_anime_data"