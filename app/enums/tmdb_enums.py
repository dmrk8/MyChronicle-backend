from enum import Enum

class TmdbMovieSortOptions(str, Enum):
    POPULARITY_DESC = "popularity.desc"
    POPULARITY_ASC = "popularity.asc"
    VOTE_AVERAGE_DESC = "vote_average.desc"
    VOTE_AVERAGE_ASC = "vote_average.asc"
    RELEASE_DATE_DESC = "primary_release_date.desc"
    RELEASE_DATE_ASC = "primary_release_date.asc"
    TITLE_ASC = "title.asc"
    TITLE_DESC = "title.desc"


class TmdbTvSortOptions(str, Enum):
    POPULARITY_DESC = "popularity.desc"
    POPULARITY_ASC = "popularity.asc"
    VOTE_AVERAGE_DESC = "vote_average.desc"
    VOTE_AVERAGE_ASC = "vote_average.asc"
    FIRST_AIR_DATE_DESC = "first_air_date.desc"
    FIRST_AIR_DATE_ASC = "first_air_date.asc"
    NAME_ASC = "name.asc"
    NAME_DESC = "name.desc"
    
class TMDBTVStatus(str, Enum):
    RETURNING_SERIES = "Returning Series"
    ENDED = "Ended"
    CANCELLED = "Cancelled"   
