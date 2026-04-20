from typing import Optional
from app.models.api.omdb_models import OMDbData
from app.repositories.media_repository import MediaRepository
from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.media_db_models import (
    MediaDB,
    MediaUpdate,
)
from app.models.api.tmdb_models import (
    TMDBMovieDetail,
    TMDBTVDetail,
)
from app.models.api.anilist_models import AnilistMediaDetailed
from app.utils.media_db_normalizer import MediaDBNormalizer


class MediaDatabaseService:
    def __init__(self, repository: MediaRepository):
        self.repository = repository

    async def create_anilist_detail(
        self, anilist_media: AnilistMediaDetailed
    ) -> MediaDB:
        media_insert = MediaDBNormalizer.normalize_anilist_to_media_core(anilist_media)
        return await self.repository.insert_media(media_insert)

    async def create_tmdb_movie_detail(
        self, tmdb_movie: TMDBMovieDetail, omdb_data: Optional[OMDbData] = None
    ) -> MediaDB:
        media_insert = MediaDBNormalizer.normalize_tmdb_movie_to_media_core(tmdb_movie, omdb_data)
        return await self.repository.insert_media(media_insert)

    async def create_tmdb_tv_detail(
        self, tmdb_tv: TMDBTVDetail, omdb_data: Optional[OMDbData] = None
    ) -> MediaDB:
        media_insert = MediaDBNormalizer.normalize_tmdb_tv_to_media_core(tmdb_tv, omdb_data)
        return await self.repository.insert_media(media_insert)

    async def get_media_by_external_id_and_source(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[MediaDB]:
        return await self.repository.get_media_by_external_id_and_source_and_media_type(
            external_id, external_source, media_type
        )

    async def update_media_by_external_id_and_source(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
        update_dict: MediaUpdate,
    ) -> Optional[MediaDB]:
        return (
            await self.repository.update_media_by_external_id_and_source_and_media_type(
                external_id, external_source, media_type, update_dict
            )
        )

    async def delete_media_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> bool:
        return (
            await self.repository.delete_media_by_external_id_and_source_and_media_type(
                external_id, external_source, media_type
            )
        )
