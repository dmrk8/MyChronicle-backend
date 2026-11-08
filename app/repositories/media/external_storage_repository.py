from typing import Optional
from app.enums.media_enums import StoredDataType
from app.models.db.external_storage_models import (
    ExternalDataDB,
    ExternalDataUpsert,
)
from app.repositories._base_repository import UpsertRepository

from app.utils.time_helpers import utc_now


class ExternalStorageRepository(UpsertRepository[ExternalDataDB]):
    db_model = ExternalDataDB

    def _key(self, payload_type: StoredDataType, external_id: str) -> str:
        return f"{payload_type.value}:{external_id}"
    
    async def upsert(self, d: ExternalDataUpsert) -> ExternalDataDB:
        now = utc_now()
        
        update_doc = {
            "$set": {
                "payload_type": d.payload_type,
                "payload": d.payload,
                "expires_at": d.expires_at,
                "updated_at": now,
            },
            "$setOnInsert": {
                "created_at": now,
            },
        }

        return await self._upsert(
            {"_id": self._key(d.payload_type, str(d.external_id))},
            update_doc,
            self._make_context(
                operation="upsert",
                external_id=d.external_id,
                payload_type=d.payload_type.value
            ),
        )

    async def get(
        self,
        payload_type: StoredDataType,
        external_id: str,
        
    ) -> Optional[ExternalDataDB]:
        return await self._find_one(
            {"_id": self._key(payload_type, external_id)},
            self._make_context(
                operation="find_one",
                external_id=external_id,
                payload_type=payload_type.value,
            ),
        )

    async def delete(
        self,
        payload_type: StoredDataType,
        external_id: str,
    ) -> bool:
        return await self._delete_one(
            {
                "_id": self._key(payload_type, external_id)
            },
            self._make_context(
                operation="delete_one",
                external_id=external_id,
                payload_type=payload_type.value,
            ),
        )
