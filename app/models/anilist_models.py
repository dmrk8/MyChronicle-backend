from pydantic import BaseModel
from typing import List, Optional


class Anilist_Media(BaseModel):
    media_id: int
    title: dict = {}
    synonyms: List[str] = []
    cover_image: Optional[str] = None
    description: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    type: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    genres: Optional[List[str]] = None
    country_of_origin: Optional[str] = None
    format: Optional[str] = None
    mean_score: Optional[int] = None
    tags: Optional[List[dict]] = None
    
class AnilistPagination(BaseModel):
    results: List[Anilist_Media]
    page: int
    per_page: int
    has_next_page: bool