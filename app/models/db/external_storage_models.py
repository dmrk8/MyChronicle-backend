from datetime import datetime, timedelta, timezone
from pyexpat import model
from turtle import update
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.enums.media_enums import (
    DataFreshnessStatus,
    MediaExternalSource,
    MediaType,
    StoredDataType,
)
from app.models.api.anilist_models import AnilistMediaDetailed
from app.models.api.omdb_models import OMDbData
from app.models.api.tmdb_models import TMDBCollection, TMDBMovieDetail, TMDBTVDetail


class MovieWithCollection(BaseModel):
    movie: TMDBMovieDetail
    collection: Optional[TMDBCollection] = None


PayloadType = AnilistMediaDetailed | MovieWithCollection | TMDBTVDetail | OMDbData


def utc_now():
    return datetime.now(timezone.utc)


class ExternalDataUpsert(BaseModel):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    payload: PayloadType
    payload_type: StoredDataType

    expires_at: Optional[datetime] = None

    freshness_status: Optional[DataFreshnessStatus] = None


class ExternalDataDB(BaseModel):
    id: str = Field(..., alias="_id")

    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    payload: AnilistMediaDetailed | MovieWithCollection | TMDBTVDetail | OMDbData
    payload_type: StoredDataType

    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    
    freshness_status: DataFreshnessStatus

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)

