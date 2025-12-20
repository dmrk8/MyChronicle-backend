from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class MediaMinimal(BaseModel):

    id: int
    source: str
    media_type: str = Field(alias="mediaType")

    title: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    average_score: Optional[float] = Field(None, alias="averageScore")

    release_date: Optional[str] = Field(None, alias="releaseDate")
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")

    format: Optional[str] = None
    episodes: Optional[int] = None
    duration: Optional[int] = None
    chapters: Optional[int] = None
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    main_studio: Optional[str] = Field(None, alias="mainStudio")
    cover_image: Optional[str] = Field(None, alias="coverImage")
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaPagination(BaseModel):
    results: List[MediaMinimal]
    current_page: int = Field(..., alias="currentPage")
    per_page: int = Field(..., alias="perPage")
    has_next_page: bool = Field(..., alias="hasNextPage")
    total: int

    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)
