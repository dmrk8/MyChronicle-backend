from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.enums.media_enums import (
    StoredDataType,
)
from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALAnimeData, MALMangaData
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import (
    TMDBCollection,
    TMDBMovieDetail,
    TMDBTVDetail,
)
from app.utils.time_helpers import utc_now

PAYLOAD_MODELS: dict[StoredDataType, type[BaseModel]] = {
    StoredDataType.ANILIST_MEDIA_DETAIL: AnilistMediaDetail,
    StoredDataType.MAL_ANIME_DATA: MALAnimeData,
    StoredDataType.MAL_MANGA_DATA: MALMangaData,
    StoredDataType.OMDB_DATA: OMDbData,
    StoredDataType.TMDB_MOVIE_DETAIL: TMDBMovieDetail,
    StoredDataType.TMDB_TV_DETAIL: TMDBTVDetail,
    StoredDataType.TMDB_COLLECTION: TMDBCollection,
}


class ExternalDataUpsert(BaseModel):
    external_id: str
    payload_type: StoredDataType

    payload: dict[str, Any]

    expires_at: Optional[datetime] = None


class ExternalDataDB(BaseModel):
    id: str = Field(..., alias="_id", description="{payload_type}:{external_id}")
    payload_type: StoredDataType

    payload: dict[str, Any]

    expires_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    @property
    def is_fresh(self) -> bool:
        return self.expires_at is None or self.expires_at > utc_now()
