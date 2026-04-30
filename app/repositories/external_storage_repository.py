from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.results import DeleteResult
from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.db_context_model import DBOpContext
from app.models.db.external_storage_models import (
    ExternalDataDB,
    ExternalDataUpsert,
)
from app.repositories._repo_observability import run_db_op
import structlog

from app.utils.time_helpers import utc_now

logger = structlog.get_logger()


class ExternalStorageRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = self.db[collection_name]
        self.logger = logger.bind(
            repository="ExternalStorageRepository", collection=collection_name
        )

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
        context = DBOpContext(
            external_id=external_data.external_id,
            external_source=external_data.external_source,
            media_type=external_data.media_type,
            operation="upsert",
            collection=self.collection.name,
        )

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

        async def _op():
            return await self.collection.find_one_and_update(
                filter_query,
                update_doc,
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_external_details_upsert",
            error_event="mongo_external_details_upsert_error",
            context=context,
        )

        return ExternalDataDB.model_validate(doc)

    async def get_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[ExternalDataDB]:
        context = DBOpContext(
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
            operation="find_one",
            collection=self.collection.name,
        )

        async def _op():
            return await self.collection.find_one(
                {
                    "external_id": external_id,
                    "external_source": external_source,
                    "media_type": media_type,
                }
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_external_details_find_one_by_external_id_source_query",
            error_event="mongo_external_details_find_one_by_external_id_source_error",
            context=context,
        )

        return ExternalDataDB.model_validate(doc) if doc else None

    async def delete_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> bool:
        async def _op() -> DeleteResult:
            return await self.collection.delete_one(
                {
                    "external_id": external_id,
                    "external_source": external_source,
                    "media_type": media_type,
                }
            )

        context = DBOpContext(
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
            operation="delete_one",
            collection=self.collection.name,
        )

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_external_details_delete_query",
            error_event="mongo_external_details_delete_one_error",
            context=context,
        )
        return result.deleted_count > 0
