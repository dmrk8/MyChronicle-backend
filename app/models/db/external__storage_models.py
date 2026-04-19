from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from app.enums.media_enums import (
    DataFreshnessStatus,
    MediaExternalSource,
    MediaType,
    StoredDataType,
    SyncFrequency,
)
from app.models.api.anilist_models import AnilistMediaDetailed
from app.models.api.omdb_models import OMDbData
from app.models.api.tmdb_models import TMDBCollection, TMDBMovieDetail, TMDBTVDetail


class MovieWithCollection(BaseModel):
    movie: TMDBMovieDetail
    collection: Optional[TMDBCollection] = None


class ExternalDataInsert(BaseModel):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType 

    fetched_at: datetime
    last_accessed_at: Optional[datetime] = None

    expires_at: Optional[datetime] = None

    payload: AnilistMediaDetailed | MovieWithCollection | TMDBTVDetail | OMDbData
    payload_type: StoredDataType

    freshness_status: Optional[DataFreshnessStatus] = None
    sync_frequency: SyncFrequency

    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values):
        now = datetime.now(timezone.utc)
        values.setdefault("last_accessed_at", now)
        values.setdefault("fetched_at", now)
        return values

    @model_validator(mode="before")
    @classmethod
    def set_status(cls, values):
        values.setdefault("freshness_status", DataFreshnessStatus.FRESH)
        return values


class ExternalDataDB(ExternalDataInsert):
    id: str = Field(..., alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return str(v)


class ExternalDataUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    freshness_status: Optional[DataFreshnessStatus] = None
    sync_frequency: Optional[SyncFrequency] = None
    payload: Optional[dict] = None
    payload_type: Optional[str] = None

    def to_update_dict(self) -> dict:
        data = self.model_dump(exclude_unset=True)
        if not data:
            raise ValueError("No fields provided for update")
        return data
