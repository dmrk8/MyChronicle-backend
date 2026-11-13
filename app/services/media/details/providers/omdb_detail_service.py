import asyncio

import structlog

from app.enums.media_enums import StoredDataType
from app.models.providers.omdb_models import OMDbData
from app.services.media.storage.external_payload_service import ExternalPayloadService
from app.services.media.sync.sync_expiry_policy import SyncExpiryPolicy
from app.services.metadata.omdb_service import OMDbService

logger = structlog.get_logger()


class OMDbDetailService:
    def __init__(
        self,
        omdb_service: OMDbService,
        external_payload_service: ExternalPayloadService,
        sync_expiry_policy: SyncExpiryPolicy,
    ):
        self.omdb_service = omdb_service
        self.external_payload_service = external_payload_service
        self.sync_expiry_policy = sync_expiry_policy
        self.logger = logger.bind(service="OMDbDetailService")

    async def get_data(self, imdb_id: str) -> OMDbData | None:
        cached = await self.external_payload_service.get(
            payload_type=StoredDataType.OMDB_DATA,
            external_id=imdb_id,
        )

        if cached:
            data = self.external_payload_service.parse_as(cached, OMDbData)
            if data and cached.is_fresh:
                return data
            if data:
                asyncio.create_task(self._refresh(imdb_id))
                return data

        return await self._refresh(imdb_id)

    async def _refresh(self, imdb_id: str) -> OMDbData | None:
        try:
            data = await self.omdb_service.fetch_data(imdb_id=imdb_id)
            if data is None:
                return None

            ttl = await self.sync_expiry_policy.calculate_omdb_sync_ttl(data)
            await self.external_payload_service.save(
                payload_type=StoredDataType.OMDB_DATA,
                external_id=imdb_id,
                model=data,
                ttl=ttl,
            )
            return data
        except Exception:
            self.logger.exception(
                "omdb_data_refresh_failed",
                imdb_id=imdb_id,
            )
            raise
