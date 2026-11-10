from typing import Optional
from uuid import UUID

from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.media_core_models import (
    MediaDB,
    MediaDBUpsert,
)

from app.repositories.media.media_core_repository import MediaCoreRepository



class MediaCoreService:
    def __init__(self, repository: MediaCoreRepository):
        self.repository = repository

    async def upsert_media(self, media_insert: MediaDBUpsert) -> MediaDB:
        return await self.repository.upsert(media_insert)

    async def get_media_by_external_ref(
        self,
        external_id: str,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[MediaDB]:
        return await self.repository.get_by_external_ref(
            external_id, external_source, media_type
        )

    async def get_media_by_internal(self, id: UUID) -> Optional[MediaDB]:
        return await self.repository.get_media_by_id(id)

