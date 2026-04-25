from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from opentelemetry import context
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import DeleteResult, InsertOneResult
from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.db_context_model import DBOpContext
from app.models.db.media_db_models import (
    MediaDB,
    MediaInsert,
    MediaUpdate,
)
from app.repositories._repo_observability import run_db_op
import structlog

logger = structlog.get_logger()


class MediaRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = self.db[collection_name]
        self.logger = logger.bind(
            repository="MediaRepository", collection=collection_name
        )

    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [("external_id", 1), ("external_source", 1), ("media_type", 1)],
            unique=True,
            name="external_unique_idx",
        )
        await self.collection.create_index("slug", unique=True)
        await self.collection.create_index("title.normalized")
        await self.collection.create_index(
            [("search_tokens", "text")], name="search_tokens_text_idx"
        )

    async def insert_media(self, media: MediaInsert) -> MediaDB:
        data = media.model_dump()
        
        context = DBOpContext(
            external_id=media.external_id,
            external_source=media.external_source,
            media_type=media.media_type,
            operation="insert_one",
            collection=self.collection.name,
        )

        async def _op() -> InsertOneResult:
            return await self.collection.insert_one(data)

        try:
            result = await run_db_op(
                self.logger,
                _op,
                success_event="mongo_media_insert_one",
                error_event="mongo_media_insert_one_error",
                context=context,
            )
            return MediaDB.model_validate({**data, "_id": result.inserted_id})

        except DuplicateKeyError:
            self.logger.warning(
                "mongo_media_insert_duplicate",
                external_id=media.external_id,
            )
            raise

    async def get_media_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[MediaDB]:
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
            success_event="mongo_media_find_one_by_external_id_and_source_and_media_type_query",
            error_event="mongo_media_find_one_by_external_id_and_source_and_media_type_error",
            context=context
        )

        if doc:
            return MediaDB.model_validate(doc)
       
        return None

    async def update_media_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
        update_dict: MediaUpdate,
    ) -> Optional[MediaDB]:
        context = DBOpContext(
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
            operation="update_one",
            collection=self.collection.name,
        )
        data = update_dict.to_update_dict()

        async def _op():
            return await self.collection.find_one_and_update(
                {
                    "external_id": external_id,
                    "external_source": external_source,
                    "media_type": media_type,
                },
                {"$set": data},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_media_update_query",
            error_event="mongo_media_update_one_error",
            context=context,
        )

        if doc:
            return MediaDB.model_validate(doc)
        return None

    async def delete_media_by_external_id_and_source_and_media_type(
        self, external_id: int, external_source: MediaExternalSource, media_type: MediaType
    ) -> bool:
        context = DBOpContext(
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
            operation="delete_one",
            collection=self.collection.name,
        )
        async def _op() -> DeleteResult:
            return await self.collection.delete_one(
                {"external_id": external_id, "external_source": external_source, "media_type": media_type}
            )

        result = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_media_delete_by_external_id_and_source_query",
            error_event="mongo_media_delete_by_external_id_and_source_error",
            context=context,
        )
        return result.deleted_count > 0
