from typing import Optional

from pydantic import BaseModel


class MediaScore(BaseModel):
    source: str
    value: float  # ALWAYS 0–100
    vote_count: Optional[int] = None


class MediaTitle(BaseModel):
    title: str
    normalized: str
    romaji: Optional[str]
    native: Optional[str]
    english: Optional[str]
    
class MediaTag(BaseModel):
    name: str
    is_media_spoiler: bool
    is_general_spoiler: bool

    # optional / extended
    rank: Optional[int] = None
    description: Optional[str] = None
