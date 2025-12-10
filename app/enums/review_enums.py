from enum import Enum


class ReviewMediaType(int, Enum):
    ANIME = 1
    MANGA = 2
    GAME = 3
    MOVIE = 4
    TV = 5


class ReviewMediaSource(int, Enum):
    ANILIST = 1
    TMDB = 2
    IGDB = 3


class ReviewStatus(str, Enum):
    PLANNING = "planning"  # Not started
    CURRENT = "current"  # In progress (reading/watching/playing)
    COMPLETED = "completed"  # Finished
    DROPPED = "dropped"  # Stopped midway
