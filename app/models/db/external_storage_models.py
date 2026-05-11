from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.enums.media_enums import (
    MediaExternalSource,
    MediaType,
    StoredDataType,
)
from app.models.db.base import DBBase
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import (
    TMDBCollection,
    TMDBMovieDetail,
    TMDBTVDetail,
)
from app.utils.time_helpers import utc_now


class MovieWithCollection(BaseModel):
    movie: TMDBMovieDetail
    collection: Optional[TMDBCollection] = None


PayloadType = AnilistMediaDetail | MovieWithCollection | TMDBTVDetail | OMDbData


class ExternalDataUpsert(BaseModel):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    payload: PayloadType
    payload_type: StoredDataType

    expires_at: Optional[datetime] = None


class ExternalDataDB(DBBase):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    payload: AnilistMediaDetail | MovieWithCollection | TMDBTVDetail | OMDbData
    payload_type: StoredDataType

    expires_at: Optional[datetime] = Field(None,
        description="If data is None, it never expires or handled manually. If set, it is considered stale after this time and should be refreshed on next access.   "
    )

    @property
    def is_fresh(self) -> bool:
        if self.expires_at is None:
            return True
        return self.expires_at > utc_now()
