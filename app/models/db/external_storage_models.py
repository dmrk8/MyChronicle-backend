from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.enums.media_enums import (
    MediaExternalSource,
    MediaType,
    StoredDataType,
)
from app.models.db.base import MongoBase
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse
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


PayloadModel = (
    AnilistMediaDetail
    | MovieWithCollection
    | TMDBTVDetail
    | OMDbData
    | MALAnimeResponse
    | MALMangaResponse
)


class ExternalDataUpsert(BaseModel):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    payload: PayloadModel
    payload_type: StoredDataType

    expires_at: Optional[datetime] = None


class ExternalDataDB(MongoBase):
    external_id: int
    external_source: MediaExternalSource
    media_type: MediaType

    payload: PayloadModel
    payload_type: StoredDataType

    expires_at: Optional[datetime] = Field(
        None,
        description="If data is None, it never expires or handled manually. If set, it is considered stale after this time and should be refreshed on next access.   ",
    )

    @property
    def is_fresh(self) -> bool:
        if self.expires_at is None:
            return True
        return self.expires_at > utc_now()
