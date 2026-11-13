import asyncio

import structlog

from app.enums.media_enums import StoredDataType
from app.models.providers.mal_models import MALAnimeResponse, MALMangaResponse
from app.services.media.storage.external_payload_service import ExternalPayloadService
from app.services.media.sync.sync_expiry_policy import SyncExpiryPolicy
from app.services.metadata.jikan_service import JikanService

logger = structlog.get_logger()


class MALDetailService:
    def __init__(
        self,
        jikan_service: JikanService,
        external_payload_service: ExternalPayloadService,
        sync_expiry_policy: SyncExpiryPolicy,
    ):
        self.jikan_service = jikan_service
        self.external_payload_service = external_payload_service
        self.sync_expiry_policy = sync_expiry_policy
        self.logger = logger.bind(service="MALDetailService")

    async def get_anime_detail(self, mal_id: int) -> MALAnimeResponse:
        return await self._get_anime_or_refresh(mal_id)

    async def get_manga_detail(self, mal_id: int) -> MALMangaResponse:
        return await self._get_manga_or_refresh(mal_id)

    async def _get_anime_or_refresh(self, mal_id: int) -> MALAnimeResponse:
        cached = await self.external_payload_service.get(
            payload_type=StoredDataType.MAL_ANIME_DATA,
            external_id=str(mal_id),
        )

        if cached:
            data = self.external_payload_service.parse_as(
                cached,
                MALAnimeResponse,
            )

            if data and cached.is_fresh:
                return data

            if data:
                asyncio.create_task(self._refresh_anime(mal_id))
                return data

        return await self._refresh_anime(mal_id)

    async def _get_manga_or_refresh(self, mal_id: int) -> MALMangaResponse:
        cached = await self.external_payload_service.get(
            payload_type=StoredDataType.MAL_MANGA_DATA,
            external_id=str(mal_id),
        )

        if cached:
            data = self.external_payload_service.parse_as(
                cached,
                MALMangaResponse,
            )

            if data and cached.is_fresh:
                return data

            if data:
                asyncio.create_task(self._refresh_manga(mal_id))
                return data

        return await self._refresh_manga(mal_id)

    async def _refresh_anime(self, mal_id: int) -> MALAnimeResponse:
        try:
            data = await self.jikan_service.get_anime_details(mal_id)
            ttl = await self.sync_expiry_policy.calculate_mal_sync_ttl(data)

            await self.external_payload_service.save(
                payload_type=StoredDataType.MAL_ANIME_DATA,
                external_id=str(mal_id),
                model=data,
                ttl=ttl,
            )

            return data
        except Exception:
            self.logger.exception(
                "mal_anime_refresh_failed",
                mal_id=mal_id,
            )
            raise

    async def _refresh_manga(self, mal_id: int) -> MALMangaResponse:
        try:
            data = await self.jikan_service.get_manga_details(mal_id)
            ttl = await self.sync_expiry_policy.calculate_mal_sync_ttl(data)

            await self.external_payload_service.save(
                payload_type=StoredDataType.MAL_MANGA_DATA,
                external_id=str(mal_id),
                model=data,
                ttl=ttl,
            )

            return data
        except Exception:
            self.logger.exception(
                "mal_manga_refresh_failed",
                mal_id=mal_id,
            )
            raise
