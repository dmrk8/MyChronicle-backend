import asyncio
from typing import Literal, overload

import structlog

from app.enums.media_enums import StoredDataType
from app.models.providers.tmdb_models import TMDBMovieDetail, TMDBTVDetail
from app.services.media.storage.external_payload_service import ExternalPayloadService
from app.services.media.sync.sync_expiry_policy import SyncExpiryPolicy
from app.services.metadata.tmdb_service import TMDBService

logger = structlog.get_logger()


class TMDBDetailService:
    def __init__(
        self,
        tmdb_service: TMDBService,
        external_payload_service: ExternalPayloadService,
        sync_expiry_policy: SyncExpiryPolicy,
    ):
        self.tmdb_service = tmdb_service
        self.external_payload_service = external_payload_service
        self.sync_expiry_policy = sync_expiry_policy
        self.logger = logger.bind(service="TMDBDetailService")

    async def get_movie_detail(self, movie_id: int) -> TMDBMovieDetail:
        return await self._get_or_refresh(movie_id, "movie")

    async def get_tv_detail(self, tv_id: int) -> TMDBTVDetail:
        return await self._get_or_refresh(tv_id, "tv")

    @overload
    async def _get_or_refresh(
        self,
        media_id: int,
        media_type: Literal["movie"],
    ) -> TMDBMovieDetail:
        ...

    @overload
    async def _get_or_refresh(
        self,
        media_id: int,
        media_type: Literal["tv"],
    ) -> TMDBTVDetail:
        ...

    async def _get_or_refresh(
        self,
        media_id: int,
        media_type: Literal["movie", "tv"],
    ) -> TMDBMovieDetail | TMDBTVDetail:
        payload_type = (
            StoredDataType.TMDB_MOVIE_DETAIL
            if media_type == "movie"
            else StoredDataType.TMDB_TV_DETAIL
        )
        model_type = TMDBMovieDetail if media_type == "movie" else TMDBTVDetail

        cached = await self.external_payload_service.get(
            payload_type=payload_type,
            external_id=str(media_id),
        )

        if cached:
            media = self.external_payload_service.parse_as(cached, model_type)
            if media and cached.is_fresh:
                return media
            if media:
                asyncio.create_task(self._refresh(media_id, media_type))
                return media

        return await self._refresh(media_id, media_type)

    async def _refresh(
        self,
        media_id: int,
        media_type: Literal["movie", "tv"],
    ) -> TMDBMovieDetail | TMDBTVDetail:
        failure_event = (
            "tmdb_movie_refresh_failed"
            if media_type == "movie"
            else "tmdb_tv_refresh_failed"
        )

        try:
            if media_type == "movie":
                media = await self.tmdb_service.get_movie_detail(media_id)
                ttl = await self.sync_expiry_policy.calculate_tmdb_movie_sync_ttl()
                payload_type = StoredDataType.TMDB_MOVIE_DETAIL
            else:
                media = await self.tmdb_service.get_tv_detail(media_id)
                ttl = await self.sync_expiry_policy.calculate_tmdb_tv_sync_ttl(media)
                payload_type = StoredDataType.TMDB_TV_DETAIL

            await self.external_payload_service.save(
                payload_type=payload_type,
                external_id=str(media_id),
                model=media,
                ttl=ttl,
            )
            return media
        except Exception:
            self.logger.exception(failure_event, media_id=media_id)
            raise
