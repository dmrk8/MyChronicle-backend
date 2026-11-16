import asyncio

import structlog

from app.core.exceptions import UpstreamServiceException
from app.enums.media_enums import StoredDataType
from app.models.providers.mal_models import MALAnimeData, MALMangaData
from app.services.media.storage.external_payload_service import ExternalPayloadService
from app.services.media.sync.sync_expiry_policy import SyncExpiryPolicy
from app.services.metadata.mal_service import MALService

logger = structlog.get_logger()


class MALDetailService:
    def __init__(
        self,
        mal_service: MALService,
        external_payload_service: ExternalPayloadService,
        sync_expiry_policy: SyncExpiryPolicy,
    ):
        self.mal_service = mal_service
        self.external_payload_service = external_payload_service
        self.sync_expiry_policy = sync_expiry_policy
        self.logger = logger.bind(service="MALDetailService")

    async def get_anime_detail(self, mal_id: int) -> MALAnimeData | None:
        return await self._get_anime_or_refresh(mal_id)

    async def get_manga_detail(self, mal_id: int) -> MALMangaData | None:
        return await self._get_manga_or_refresh(mal_id)

    async def _get_anime_or_refresh(self, mal_id: int) -> MALAnimeData | None:
        cached = await self.external_payload_service.get(
            payload_type=StoredDataType.MAL_ANIME_DATA,
            external_id=str(mal_id),
        )

        if cached:
            data = self.external_payload_service.parse_as(
                cached,
                MALAnimeData,
            )

            if data and cached.is_fresh:
                return data

            if data:
                asyncio.create_task(self._refresh_anime(mal_id))
                return data

        return await self._refresh_anime(mal_id)

    async def _get_manga_or_refresh(self, mal_id: int) -> MALMangaData | None:
        cached = await self.external_payload_service.get(
            payload_type=StoredDataType.MAL_MANGA_DATA,
            external_id=str(mal_id),
        )

        if cached:
            data = self.external_payload_service.parse_as(
                cached,
                MALMangaData,
            )

            if data and cached.is_fresh:
                return data

            if data:
                asyncio.create_task(self._refresh_manga(mal_id))
                return data

        return await self._refresh_manga(mal_id)

    async def _refresh_anime(self, mal_id: int) -> MALAnimeData | None:
        try:
            data = await self.mal_service.get_anime_details(mal_id)
            ttl = await self.sync_expiry_policy.calculate_mal_sync_ttl()

            await self.external_payload_service.save(
                payload_type=StoredDataType.MAL_ANIME_DATA,
                external_id=str(mal_id),
                model=data,
                ttl=ttl,
            )
            return data

        except UpstreamServiceException:
            self.logger.warning(
                "mal_anime_unavailable",
                mal_id=mal_id,
            )
            return None

        except Exception:
            self.logger.exception(
                "mal_anime_refresh_failed",
                mal_id=mal_id,
            )
            raise

    async def _refresh_manga(self, mal_id: int) -> MALMangaData | None:
        try:
            data = await self.mal_service.get_manga_details(mal_id)
            ttl = await self.sync_expiry_policy.calculate_mal_sync_ttl()

            await self.external_payload_service.save(
                payload_type=StoredDataType.MAL_MANGA_DATA,
                external_id=str(mal_id),
                model=data,
                ttl=ttl,
            )
            return data

        except UpstreamServiceException:
            self.logger.warning(
                "mal_manga_unavailable",
                mal_id=mal_id,
            )
            return None

        except Exception:
            self.logger.exception(
                "mal_manga_refresh_failed",
                mal_id=mal_id,
            )
            raise
