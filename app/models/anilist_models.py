from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class AnilistMedia(BaseModel):
    media_id: int = Field(..., alias="mediaId")
    title: dict = {}
    synonyms: List[str] = []
    cover_image: Optional[str] = Field(None, alias="coverImage")
    description: Optional[str] = None
    start_year: Optional[int] = Field(None, alias="startYear")
    end_year: Optional[int] = Field(None, alias="endYear")
    type: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    genres: Optional[List[str]] = None
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    format: Optional[str] = None
    mean_score: Optional[int] = Field(None, alias="meanScore")
    tags: Optional[List[dict]] = None
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

class Title(BaseModel):
    english: Optional[str] = None
    romaji: Optional[str] = None
    native: Optional[str] = None

class NextAiringEpisode(BaseModel):
    episode: Optional[int] = None
    airing_at: Optional[int] = Field(None, alias="airingAt")
    time_until_airing: Optional[int] = Field(None, alias="timeUntilAiring")
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
class AnilistMediaMinimal(BaseModel):
    id: int = Field(..., alias="id")
    title: Title 
    format: Optional[str] = None
    genres: Optional[List[str]] = None
    episodes: Optional[int] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    next_airing_episode: Optional[NextAiringEpisode] = Field(None, alias="nextAiringEpisode")
    main_studio: Optional[str] = Field(None, alias="mainStudio")
    cover_image_large: Optional[str] = Field(None, alias="coverImageLarge")
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")
    average_score: Optional[int] = Field(None, alias="averageScore")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

class AnilistPagination(BaseModel):
    results: List[AnilistMedia]
    page: int
    per_page: int = Field(..., alias="perPage")
    has_next_page: bool = Field(..., alias="hasNextPage")
    
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

