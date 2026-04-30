from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.enums.media_enums import (
    MediaExternalSource,
    MediaType,
)


class MediaScore(BaseModel):
    source: str
    value: float  # ALWAYS 0–100
    vote_count: Optional[int] = None


class MediaTag(BaseModel):
    name: str
    is_media_spoiler: bool
    is_general_spoiler: bool

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)


class MediaTitle(BaseModel):
    title: str
    normalized: str
    romaji: Optional[str]
    native: Optional[str]
    english: Optional[str]


class MediaUpsert(BaseModel):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    # base
    title: MediaTitle
    search_tokens: List[str]

    description: Optional[str] = None

    is_adult: bool = False
    status: Optional[str] = None
    format: Optional[str] = None

    season: Optional[str] = None
    season_year: Optional[int] = None

    release_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    cover_image: Optional[str] = None
    banner_image: Optional[str] = None

    scores: Optional[List[MediaScore]] = Field(
        None,
        description="Computed / externally aggregated field. Managed separately from primary media ingestion pipeline.",
    )

    popularity: Optional[float] = None

    genres: Optional[List[str]] = None
    tags: Optional[List[MediaTag]] = None
    keywords: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None

    slug: Optional[str] = None


class MediaDB(BaseModel):
    id: str = Field(..., alias="_id")

    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    title: MediaTitle
    search_tokens: List[str]

    description: Optional[str] = None

    is_adult: bool
    status: Optional[str] = None
    format: Optional[str] = None

    season: Optional[str] = None
    season_year: Optional[int] = None

    release_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    cover_image: Optional[str] = None
    banner_image: Optional[str] = None

    scores: Optional[List[MediaScore]] = None
    popularity: Optional[float] = None

    genres: Optional[List[str]] = None
    tags: Optional[List[MediaTag]] = None
    keywords: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None

    slug: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)


