from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

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
    vote_count: Optional[int] = Field(None, alias="voteCount")
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaTitle(BaseModel):
    title: str
    normalized: str
    romaji: Optional[str] = None
    native: Optional[str] = None
    english: Optional[str] = None


class MediaTag(BaseModel):
    name: str

    # optional / extended
    is_media_spoiler: Optional[bool] = Field(None, alias="isMediaSpoiler")
    is_general_spoiler: Optional[bool] = Field(None, alias="isGeneralSpoiler")
    rank: Optional[int] = None
    description: Optional[str] = None
    category: Optional[str] = None
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
