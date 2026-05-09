from typing import Optional
from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.external_storage_models import (
    ExternalDataDB,
    ExternalDataUpsert,
)
from app.repositories._base_repository import UpsertRepository

from app.utils.time_helpers import utc_now

class ExternalStorageRepository(UpsertRepository[ExternalDataDB]):
    db_model = ExternalDataDB

    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [
                ("external_id", 1),
                ("external_source", 1),
                ("media_type", 1),
            ],
            unique=True,
            name="external_id_source_media_type_idx",
        )
        await self.collection.create_index("expires_at", name="expires_at_idx")
        await self.collection.create_index(
            "last_accessed_at", name="last_accessed_at_idx"
        )

    async def upsert(self, external_data: ExternalDataUpsert) -> ExternalDataDB:
        filter_query = {
            "external_id": external_data.external_id,
            "external_source": external_data.external_source,
            "media_type": external_data.media_type,
        }
        now = utc_now()

        data = external_data.model_dump(
            exclude_none=True, exclude={"external_id", "external_source", "media_type"}
        )
        update_doc = {
            "$set": {
                **data,
                "updated_at": now,
            },
            "$setOnInsert": {
                "external_id": external_data.external_id,
                "external_source": external_data.external_source,
                "media_type": external_data.media_type,
                "created_at": now,
            },
        }

        return await self._upsert(
            filter_query,
            update_doc,
            self._make_context(
                operation="upsert",
                external_id=external_data.external_id,
                external_source=external_data.external_source,
                media_type=external_data.media_type,
            ),
        )

    async def get_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[ExternalDataDB]:
        filter_query = {
            "external_id": external_id,
            "external_source": external_source,
            "media_type": media_type,
        }

        return await self._find_one(
            filter_query,
            self._make_context(
                operation="find_one",
                external_id=external_id,
                external_source=external_source,
                media_type=media_type,
            ),
        )

    async def delete_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> bool:
        return await self._delete_one(
            {
                "external_id": external_id,
                "external_source": external_source,
                "media_type": media_type,
            },
            self._make_context(
                operation="delete_one",
                external_id=external_id,
                external_source=external_source,
                media_type=media_type,
            ),
        )
