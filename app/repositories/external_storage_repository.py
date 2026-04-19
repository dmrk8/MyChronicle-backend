from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.results import DeleteResult, InsertOneResult
from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.external__storage_models import (
    ExternalDataDB,
    ExternalDataInsert,
    ExternalDataUpdate,
)
from app.repositories._repo_observability import run_db_op
import structlog

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
            name="external_id_source_unique_idx",
        )
        await self.collection.create_index("expires_at", name="expires_at_idx")
        await self.collection.create_index(
            "last_accessed_at", name="last_accessed_at_idx"
        )

    async def upsert(self, details: ExternalDataInsert) -> ExternalDataDB:
        data = details.model_dump()

        async def _op():
            return await self.collection.find_one_and_update(
                {
                    "external_id": details.external_id,
                    "external_source": details.external_source,
                    "media_type": details.media_type,
                },
                {
                    "$set": {
                        "payload": data["payload"],
                        "payload_type": data["payload_type"],
                        "expires_at": data["expires_at"],
                        "fetched_at": data["fetched_at"],
                        "freshness_status": data["freshness_status"],
                        "sync_frequency": data["sync_frequency"],
                    },
                    "$setOnInsert": {
                        "external_id": data["external_id"],
                        "external_source": data["external_source"],
                    },
                },
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_external_details_upsert",
            error_event="mongo_external_details_upsert_error",
            context={
                "external_id": details.external_id,
                "external_source": details.external_source,
                "media_type": details.media_type,
            },
        )

        return ExternalDataDB.model_validate(doc)

    async def get_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[ExternalDataDB]:
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
            context={
                "external_id": external_id,
                "external_source": str(external_source),
                "media_type": str(media_type),
            },
        )

        if doc:
            return ExternalDataDB.model_validate(doc)
        return None

    async def update_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
        update: ExternalDataUpdate,
    ) -> Optional[ExternalDataDB]:
        update_dict = update.to_update_dict()

        async def _op():
            return await self.collection.find_one_and_update(
                {"external_id": external_id, "external_source": external_source, "media_type": media_type},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_external_details_update_query",
            error_event="mongo_external_details_update_one_error",
            context={
                "external_id": external_id,
                "external_source": str(external_source),
                "media_type": str(media_type),
            },
        )

        if doc:
            return ExternalDataDB.model_validate(doc)
        return None

    async def delete_by_external_id_and_source_and_media_type(
        self, external_id: int, external_source: MediaExternalSource, media_type: MediaType
    ) -> bool:
        async def _op() -> DeleteResult:
            return await self.collection.delete_one(
                {"external_id": external_id, "external_source": external_source, "media_type": media_type}
            )

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_external_details_delete_query",
            error_event="mongo_external_details_delete_one_error",
            context={
                "external_id": external_id,
                "external_source": str(external_source),
                "media_type": str(media_type),
            },
        )
        return result.deleted_count > 0
