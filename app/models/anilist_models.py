from pydantic import BaseModel, Field
from typing import List, Optional

class Anilist_Media(BaseModel):
    media_id: int = Field(..., serialization_alias="mediaId")
    title: dict = {}
    synonyms: List[str] = []
    cover_image: Optional[str] = Field(None, serialization_alias="coverImage")
    description: Optional[str] = None
    start_year: Optional[int] = Field(None, serialization_alias="startYear")
    end_year: Optional[int] = Field(None, serialization_alias="endYear")
    type: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    genres: Optional[List[str]] = None
    country_of_origin: Optional[str] = Field(None, serialization_alias="countryOfOrigin")
    format: Optional[str] = None
    mean_score: Optional[int] = Field(None, serialization_alias="meanScore")
    tags: Optional[List[dict]] = None

class AnilistPagination(BaseModel):
    results: List[Anilist_Media]
    page: int
    per_page: int = Field(..., serialization_alias="perPage")
    has_next_page: bool = Field(..., serialization_alias="hasNextPage")

    