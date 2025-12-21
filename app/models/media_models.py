from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class MediaMinimal(BaseModel):

    id: int
    media_source: str = Field(alias="mediaSource")
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
    per_page: Optional[int] = Field(None, alias="perPage")
    has_next_page: bool = Field(..., alias="hasNextPage")
    total: Optional[int] = None

    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)


class MediaDetailed(BaseModel):
    id: int
    media_source: str = Field(alias="mediaSource")
    media_type: Optional[str] = None

    title: Optional[str] = None
    genres: Optional[List[str]] = None
    status: Optional[str] = None
    average_score: Optional[float] = Field(None, alias="averageScore")
    description: Optional[str] = None
    
    is_adult: Optional[bool] = Field(None, alias="isAdult")
    source: Optional[str] = None
    format: Optional[str] = None
    episodes: Optional[int] = None
    seasons: Optional[int] = None
    duration: Optional[int] = None
    volumes: Optional[int] = None
    chapters: Optional[int] = None
    country_of_origin: Optional[str] = Field(None, alias="countryOfOrigin")
    status: Optional[str] = None
    synonyms: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    # relations: Relations = Relations(edges=[])

    release_date: Optional[str] = Field(None, alias="releaseDate")
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    season: Optional[str] = None
    season_year: Optional[int] = Field(None, alias="seasonYear")

    cover_image: Optional[str] = Field(None, alias="coverImage")
    banner_image: Optional[str] = Field(None, alias="bannerImage")

    main_studio: Optional[str] = Field(None, alias="mainStudio")
    studios: Optional[List[str]] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
