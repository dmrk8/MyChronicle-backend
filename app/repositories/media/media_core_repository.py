from typing import Optional

from uuid import UUID
from app.utils.uuid_helpers import new_uuid

from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.media_core_models import (
    MediaDB,
    MediaDBUpsert,
)
from app.repositories._base_repository import UpsertRepository

from app.utils.time_helpers import utc_now

MEDIA_SCHEMA_VERSION = 1


class MediaCoreRepository(UpsertRepository[MediaDB]):
    db_model = MediaDB

    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [
                ("primary_external_id", 1),
                ("primary_external_source", 1),
                ("media_type", 1),
            ],
            unique=True,
            name="primary_external_id_source_type_idx",
        )

    async def upsert(self, m: MediaDBUpsert) -> MediaDB:
        now = utc_now()

        update_doc = {
            "$set": {
                "last_sync_at": now,
                "updated_at": now,
                "schema_version": MEDIA_SCHEMA_VERSION,
            },
            "$addToSet": {
                "external_ids": {
                    "$each": [
                        reference.model_dump(mode="json")
                        for reference in m.external_ids
                    ]
                }
            },
            "$setOnInsert": {
                "_id": new_uuid(),
                "primary_external_id": m.primary_external_id,
                "primary_external_source": m.primary_external_source,
                "media_type": m.media_type,
                "created_at": now,
            },
        }
        return await self._upsert(
            {
                "primary_external_id": m.primary_external_id,
                "primary_external_source": m.primary_external_source,
                "media_type": m.media_type,
            },
            update_doc,
            self._make_context(
                operation="upsert_media",
                external_id=m.primary_external_id,
                external_source=m.primary_external_source,
                media_type=m.media_type,
            ),
        )

    async def get_media_by_id(self, id: UUID) -> Optional[MediaDB]:
        return await self._find_one(
            {"_id": id},
            self._make_context(operation="find_one_by_id", id=str(id)),
        )

    async def get_by_external_ref(
        self,
        external_id: str,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[MediaDB]:

        return await self._find_one(
            {
                "primary_external_id": external_id,
                "primary_external_source": external_source,
                "media_type": media_type,
            },
            self._make_context(
                operation="find_one_by_external_id_and_source_and_media_type",
                external_id=external_id,
                external_source=external_source,
                media_type=media_type,
            ),
        )

