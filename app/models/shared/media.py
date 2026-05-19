from enum import Enum
from typing import Optional

from pydantic import BaseModel

class MediaScoreSource(str, Enum):
    ANILIST = "ANILIST"
    MAL = "MAL"
    TMDB = "TMDB"
    IMDB = "IMDB"
    METACRITIC = "METACRITIC"
    ROTTEN_TOMATOES = "ROTTEN_TOMATOES"
    
class MediaScore(BaseModel):
    source: MediaScoreSource
    value: float  # ALWAYS 0–100
    vote_count: Optional[int] = None


class MediaTitle(BaseModel):
    title: str
    normalized: str
    romaji: Optional[str] = None
    native: Optional[str] = None
    english: Optional[str] = None


class MediaTag(BaseModel):
    name: str

    # optional / extended
    is_media_spoiler: Optional[bool] = None
    is_general_spoiler: Optional[bool] = None
    rank: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = None
