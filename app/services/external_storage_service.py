from datetime import datetime

import structlog
from typing import Optional

from app.enums.media_enums import (
    MediaExternalSource,
    MediaType,
    StoredDataType,
)
from app.models.db.external_storage_models import (
    ExternalDataDB,
    ExternalDataUpsert,
    PayloadType,
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

    async def get_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[ExternalDataDB]:
        return await self.repository.get_by_external_id_and_source_and_media_type(
            external_id, external_source, media_type
        )

    async def delete(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> None:
        await self.repository.delete_by_external_id_and_source_and_media_type(
            external_id, external_source, media_type
        )
        self.logger.debug(
            "Deleted external data",
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
        )

    async def upsert(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
        payload: PayloadType,
        payload_type: StoredDataType,
        expires_at: Optional[datetime] = None,
    ) -> ExternalDataDB:

        insert_model = ExternalDataUpsert(
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
            payload=payload,
            payload_type=payload_type,
            expires_at=expires_at,
        )

        res = await self.repository.upsert(insert_model)

        self.logger.debug(
            "Upserted external data",
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
        )
        return res
