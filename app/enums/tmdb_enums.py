from enum import Enum


class TMDBSortOption(str, Enum):
    POPULARITY_DESC = "popularity.desc"
    TRENDING_DESC = "TRENDING_DESC"
    IMDB_DESC = "IMDB_DESC"