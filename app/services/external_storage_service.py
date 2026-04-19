from datetime import timedelta, timezone, datetime
import time

import structlog
from typing import Optional

from app.enums.media_enums import MediaExternalSource, MediaType, SyncFrequency
from app.models.db.external__storage_models import (
    ExternalDataDB,
    ExternalDataInsert,
    ExternalDataUpdate,
)
from app.repositories.external_storage_repository import ExternalStorageRepository

logger = structlog.get_logger()


class ExternalStorageService:
    def __init__(
        self,
        repository: ExternalStorageRepository,
    ):
        self.repository = repository
        self.logger = logger.bind(service="ExternalStorageService")

    def _compute_expiry(self, sync_frequency: SyncFrequency) -> Optional[datetime]:
        now = datetime.now(timezone.utc)

        mapping = {
            SyncFrequency.HIGH: timedelta(hours=6),
            SyncFrequency.MEDIUM: timedelta(days=1),
            SyncFrequency.LOW: timedelta(days=7),
            SyncFrequency.MANUAL: None,
        }

        ttl = mapping.get(sync_frequency)

        return now + ttl if ttl else None

    def _is_stale(self, entry: ExternalDataDB) -> bool:
        if not entry.expires_at:
            return False
        return datetime.now(timezone.utc) > entry.expires_at

    async def get_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[ExternalDataDB]:
        entry = await self.repository.get_by_external_id_and_source_and_media_type(
            external_id, external_source, media_type
        )

        if entry:
            await self.repository.update_by_external_id_and_source_and_media_type(
                external_id,
                external_source,
                media_type,
                ExternalDataUpdate(last_accessed_at=datetime.now(timezone.utc)),
            )
            return entry
        return None

    async def update(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
        update: ExternalDataUpdate,
    ) -> Optional[ExternalDataDB]:
        return await self.repository.update_by_external_id_and_source_and_media_type(
            external_id, external_source, media_type, update
        )

    async def delete(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> bool:
        return await self.repository.delete_by_external_id_and_source_and_media_type(
            external_id, external_source, media_type
        )

    async def upsert(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
        sync_frequency: SyncFrequency,
        payload: dict,
        payload_type: str,
        expires_at: Optional[datetime] = None,
    ) -> ExternalDataDB:

        if expires_at is None:
            expires_at = self._compute_expiry(sync_frequency)

        insert_model = ExternalDataInsert(
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
            sync_frequency=sync_frequency,
            payload=payload,
            payload_type=payload_type,
            expires_at=expires_at,
        )  # type: ignore

        return await self.repository.upsert(insert_model)
