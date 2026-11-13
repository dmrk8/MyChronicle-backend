from app.models.db.media_core_models import (
    MediaDB,
    MediaDBUpsert,
)

from app.models.providers.anilist_models import AnilistMediaDetail
from app.models.providers.mal_models import MALMangaResponse, MALMangaResponse
from app.models.providers.mal_models import MALAnimeResponse
from app.models.providers.omdb_models import OMDbData
from app.models.providers.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.services.media.core.media_core_service import MediaCoreService
from app.utils.normalizers.media_core_normalizer import MediaDBNormalizer


class MediaCoreEnsureService:
    def __init__(self, service: MediaCoreService):
        self.service = service

    async def ensure_anilist(
        self,
        anilist: AnilistMediaDetail,
        mal: MALAnimeResponse | MALMangaResponse | None = None,
    ) -> MediaDB:
        data = MediaDBNormalizer.normalize_ani(anilist, mal)
        return await self._get_or_create(data)

    async def ensure_tmdb_movie(
        self,
        movie: TMDBMovieDetail,
        omdb: OMDbData | None = None,
    ) -> MediaDB:
        data = MediaDBNormalizer.normalize_movie(movie, omdb)
        return await self._get_or_create(data)

    async def ensure_tmdb_tv(
        self,
        tv: TMDBTVDetail,
        omdb: OMDbData | None = None,
    ) -> MediaDB:
        data = MediaDBNormalizer.normalize_tv(tv, omdb)
        return await self._get_or_create(data)

    async def _get_or_create(self, data: MediaDBUpsert) -> MediaDB:
        existing = await self.service.get_media_by_external_ref(
            data.primary_external_id,
            data.primary_external_source,
            data.media_type,
        )

        if existing:
            return existing

        return await self.service.upsert_media(data)
