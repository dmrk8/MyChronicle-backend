from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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


class MediaInsert(BaseModel):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None

    # base
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

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
    )

    @model_validator(mode="before")
    def ensure_tokens(cls, values):
        if "search_tokens" not in values:
            raise ValueError("search_tokens must be provided")
        return values

    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values):
        now = datetime.now(timezone.utc)
        values.setdefault("created_at", now)
        values.setdefault("updated_at", now)
        values.setdefault("last_synced_at", now)
        values.setdefault("scores_last_synced", now)

        return values


class MediaDB(MediaInsert):
    id: str = Field(..., alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)


class MediaUpdate(BaseModel):
    status: Optional[str] = None
    format: Optional[str] = None
    season: Optional[str] = None
    season_year: Optional[int] = None
    release_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    cover_image: Optional[str] = None
    banner_image: Optional[str] = None
    description: Optional[str] = None
    popularity: Optional[float] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[MediaTag]] = None
    keywords: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    slug: Optional[str] = None
    average_score: Optional[float] = None

    def to_update_dict(self) -> dict:
        data = self.model_dump(exclude_unset=True)
        if not data:
            raise ValueError("No fields provided for update")
        now = datetime.now(timezone.utc)
        data["updated_at"] = now
        return data
