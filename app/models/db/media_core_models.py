from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from app.enums.media_enums import (
    MediaExternalSource,
    MediaType,
)
from app.models.db.base import DBBase
from app.models.shared.media import MediaScore, MediaTag, MediaTitle


class ExternalReference(BaseModel):
    id: str
    source: MediaExternalSource


class MediaDBUpsert(BaseModel):
    primary_id: int
    primary_source: MediaExternalSource
    media_type: MediaType
    
    external_ids: List[ExternalReference]

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
        description="Computed / externally aggregated field.\n"
        "Managed separately from primary media ingestion pipeline.",
    )

    popularity: Optional[float] = None

    genres: Optional[List[str]] = None
    tags: Optional[List[MediaTag]] = None
    keywords: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    alternative_titles: Optional[List[str]] = None

    slug: Optional[str] = None


class MediaDB(DBBase):
    external_ids: List[ExternalReference]
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
