from datetime import timedelta, timezone, datetime

import structlog
from typing import Optional

from app.models.db.media_external_details_models import (
    MediaExternalDetailsDB,
    MediaExternalDetailsInsert,
    MediaExternalDetailsUpdate,
)
from app.repositories.media_external_details_repository import (
    MediaExternalDetailsRepository,
)
from app.enums.media_enums import MediaExternalSource, SyncFrequency

logger = structlog.get_logger()


class MediaExternalDetailsService:
    def __init__(
        self,
        repository: MediaExternalDetailsRepository,
    ):
        self.repository = repository
        self.logger = logger.bind(service="MediaExternalDetailsService")

    def _compute_expiry(self, sync_frequency: SyncFrequency) -> Optional[datetime]:
        now = datetime.now(timezone.utc)

        mapping = {
            SyncFrequency.HIGH: timedelta(hours=1),
            SyncFrequency.MEDIUM: timedelta(days=1),
            SyncFrequency.LOW: None,
            SyncFrequency.MANUAL: None,
        }

        ttl = mapping.get(sync_frequency)

        return now + ttl if ttl else None

    def _is_stale(self, entry: MediaExternalDetailsDB) -> bool:
        if not entry.expires_at:
            return False
        return datetime.now(timezone.utc) > entry.expires_at

    async def get_by_external_id_and_source(
        self, external_id: int, external_source: MediaExternalSource
    ) -> Optional[MediaExternalDetailsDB]:
        entry = await self.repository.get_by_external_id_and_source(
            external_id, external_source
        )

        if entry:
            await self.repository.update(
                external_id,
                external_source,
                MediaExternalDetailsUpdate(last_accessed_at=datetime.now(timezone.utc)),
            )
            return entry
        return None

    async def update(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        update: MediaExternalDetailsUpdate,
    ) -> Optional[MediaExternalDetailsDB]:
        return await self.repository.update(external_id, external_source, update)

    async def delete(
        self, external_id: int, external_source: MediaExternalSource
    ) -> bool:
        return await self.repository.delete(external_id, external_source)

    async def upsert(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        sync_frequency: SyncFrequency,
        payload: dict,
        payload_type: str,
    ) -> MediaExternalDetailsDB:

        expires_at = self._compute_expiry(sync_frequency)

        insert_model = MediaExternalDetailsInsert(
            external_id=external_id,
            external_source=external_source,
            sync_frequency=sync_frequency,
            payload=payload,
            payload_type=payload_type,
            expires_at=expires_at,
        )  # type: ignore

        return await self.repository.upsert(insert_model)
