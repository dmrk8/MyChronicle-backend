from typing import List, List, Optional
from uuid import UUID

import structlog
from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.media_core_models import (
    MediaDB,
)

from app.models.shared.media import MediaScore

from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALMangaResponse, MALMangaResponse
from app.models.providers.mal_models import MALAnimeResponse
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.repositories.media_core_repository import MediaCoreRepository
from app.utils.normalizers.media_core_normalizer import MediaDBNormalizer

logger = structlog.get_logger()


class MediaCoreService:
    def __init__(self, repository: MediaCoreRepository):
        self.repository = repository
        self.logger = logger.bind(service="MediaCoreService")

    async def create_anime_detail(
        self,
        anilist_media: AnilistMediaDetail,
        mal_data: Optional[MALAnimeResponse] = None,
    ) -> MediaDB:
        media_insert = MediaDBNormalizer.normalize_anime_or_manga_to_media_core(
            anilist_media, mal_data
        )
        res = await self.repository.upsert(media_insert)
        self.logger.debug(
            "Inserted Anilist media into database",
            external_id=anilist_media.id,
            media_type=anilist_media.type,
        )
        return res

    async def create_manga_detail(
        self,
        anilist_media: AnilistMediaDetail,
        mal_data: Optional[MALMangaResponse] = None,
    ) -> MediaDB:
        media_insert = MediaDBNormalizer.normalize_anime_or_manga_to_media_core(
            anilist_media, mal_data
        )
        res = await self.repository.upsert(media_insert)
        self.logger.debug(
            "Inserted Anilist media into database",
            external_id=anilist_media.id,
            media_type=anilist_media.type,
        )
        return res

    async def create_movie_detail(
        self, tmdb_movie: TMDBMovieDetail, omdb_data: Optional[OMDbData] = None
    ) -> MediaDB:
        media_insert = MediaDBNormalizer.normalize_tmdb_movie_to_media_core(
            tmdb_movie, omdb_data
        )
        res = await self.repository.upsert(media_insert)
        self.logger.debug(
            "Inserted TMDB movie into database",
            external_id=tmdb_movie.id,
            media_type=MediaType.MOVIE,
        )
        return res

    async def create_tv_detail(
        self, tmdb_tv: TMDBTVDetail, omdb_data: Optional[OMDbData] = None
    ) -> MediaDB:
        media_insert = MediaDBNormalizer.normalize_tmdb_tv_to_media_core(
            tmdb_tv, omdb_data
        )
        res = await self.repository.upsert(media_insert)
        self.logger.debug(
            "Inserted TMDB TV into database",
            external_id=tmdb_tv.id,
            media_type=MediaType.TV,
        )
        return res

    async def get_media(
        self,
        primary_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[MediaDB]:
        return await self.repository.get_media_by_primary_id_and_source_and_media_type(
            primary_id, external_source, media_type
        )

    async def get_media_by_internal_id(self, id: str) -> Optional[MediaDB]:
        return await self.repository.get_media_by_id(UUID(id))

    async def update_media_scores(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
        scores: List[MediaScore],
    ) -> Optional[MediaDB]:

        res = await self.repository.update_media_scores_by_primary_id_and_source_and_media_type(
            external_id, external_source, media_type, scores
        )

        self.logger.debug(
            "Updated Media Scores",
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
        )

        return res

    async def delete_media_by_primary_id_and_source_and_media_type(
        self,
        primary_id: int,
        primary_source: MediaExternalSource,
        media_type: MediaType,
    ) -> None:
        await self.repository.delete_media_by_primary_id_and_source_and_media_type(
            primary_id, primary_source, media_type
        )
        self.logger.debug(
            "Deleted Media",
            primary_id=primary_id,
            primary_source=primary_source,
            media_type=media_type,
        )
