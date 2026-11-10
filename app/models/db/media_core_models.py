from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator
from uuid import UUID
from app.enums.media_enums import (
    MediaExternalSource,
    MediaType,
)
from app.models.db.base import DBBase


class ExternalReference(BaseModel):
    id: str
    source: MediaExternalSource


class MediaDBUpsert(BaseModel):
    primary_external_id: str
    primary_external_source: MediaExternalSource
    media_type: MediaType
    external_ids: List[ExternalReference]
    
class MediaDB(DBBase):
    primary_external_id: str
    primary_external_source: MediaExternalSource
    media_type: MediaType
    external_ids: List[ExternalReference]

    schema_version: int
    last_sync_at: datetime


class MediaCore(BaseModel):
    id: str

    primary_external_id: str
    primary_external_source: MediaExternalSource
    media_type: MediaType
    external_ids: List[ExternalReference]

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
