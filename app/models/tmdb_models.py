from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class TMDBMediaMinimal(BaseModel):
    adult: bool
    backdrop_path: Optional[str] = Field(None, alias="backdropPath")
    genre_ids: List[int] = Field(..., alias="genreIds")
    id: int
    original_language: str = Field(..., alias="originalLanguage")
    popularity: float
    media_type: Optional[str] = Field(None, alias="mediaType")
    vote_average: float = Field(..., alias="voteAverage")

    # Movie-specific fields
    title: Optional[str] = None
    original_title: Optional[str] = Field(None, alias="originalTitle")
    release_date: Optional[str] = Field(None, alias="releaseDate")

    # TV-specific fields
    name: Optional[str] = None
    original_name: Optional[str] = Field(None, alias="originalName")
    first_air_date: Optional[str] = Field(None, alias="firstAirDate")
    origin_country: Optional[List[str]] = Field(None, alias="originCountry")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBPageInfo(BaseModel):
    page: int
    total_pages: int = Field(..., alias="totalPages")
    total_results: int = Field(..., alias="totalResults")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class TMDBPagination(BaseModel):
    results: List[TMDBMediaMinimal]
    page: int
    total_pages: int = Field(..., alias="totalPages")
    total_results: int = Field(..., alias="totalResults")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
