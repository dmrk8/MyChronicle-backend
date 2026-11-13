import asyncio

import structlog

from app.enums.media_enums import StoredDataType
from app.models.providers.anilist_models import AnilistMediaDetail
from app.services.metadata.anilist_service import AnilistService
from app.services.media.storage.external_payload_service import ExternalPayloadService
from app.services.media.sync.sync_expiry_policy import SyncExpiryPolicy

logger = structlog.get_logger()


class AnilistDetailService:
    def __init__(
        self,
        anilist_service: AnilistService,
        external_payload_service: ExternalPayloadService,
        sync_expiry_policy: SyncExpiryPolicy,
    ):
        self.anilist_service = anilist_service
        self.external_payload_service = external_payload_service
        self.sync_expiry_policy = sync_expiry_policy
        self.logger = logger.bind(service="AnilistDetailService")

    async def get_media_detail(self, media_id: int) -> AnilistMediaDetail:
        cached = await self.external_payload_service.get(
            payload_type=StoredDataType.ANILIST_MEDIA_DETAIL,
            external_id=str(media_id),
        )

        if cached:
            media = self.external_payload_service.parse_as(
                cached,
                AnilistMediaDetail,
            )

            if media and cached.is_fresh:
                return media

            if media:
                asyncio.create_task(self._refresh_media_detail(media_id))
                return media

        return await self._refresh_media_detail(media_id)

    async def _refresh_media_detail(
        self,
        media_id: int,
    ) -> AnilistMediaDetail:
        try:
            media = await self.anilist_service.get_media_detail(media_id)

            ttl = await self.sync_expiry_policy.calculate_anilist_sync_ttl(
                media
            )

            await self.external_payload_service.save(
                payload_type=StoredDataType.ANILIST_MEDIA_DETAIL,
                external_id=str(media_id),
                model=media,
                ttl=ttl,
            )

            return media
        except Exception:
            self.logger.exception(
                "anilist_media_refresh_failed",
                media_id=media_id,
            )
            raise
