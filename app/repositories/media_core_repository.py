from typing import List, Optional
from pymongo import ReturnDocument
from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.db_context_model import DBOpContext
from app.models.db.media_core_models import (
    MediaDB,
    MediaScore,
    MediaDBUpsert,
)
from app.repositories._base_repository import UpsertRepository
from app.repositories._repo_observability import run_db_op

from app.utils.time_helpers import utc_now


class MediaCoreRepository(UpsertRepository[MediaDB]):
    db_model = MediaDB
    
    async def init_indexes(self) -> None:
        await self.collection.create_index(
            [("primary_id", 1), ("primary_source", 1), ("media_type", 1)],
            unique=True,
            name="external_id_source_media_type_idx",
        )
        await self.collection.create_index("slug", unique=True)
        await self.collection.create_index("title.normalized")
        await self.collection.create_index(
            [("search_tokens", "text")], name="search_tokens_text_idx"
        )

    async def upsert(self, media: MediaDBUpsert) -> MediaDB:
        now = utc_now()

        data = media.model_dump(
            exclude={"scores", "primary_id", "primary_source", "media_type"},
            exclude_none=True,
        )

        update_doc = {
            "$set": {
                **data,
                "updated_at": now,
            },
            "$setOnInsert": {
                "primary_id": media.primary_id,
                "primary_source": media.primary_source,
                "media_type": media.media_type,
                "created_at": now,
            },
        }
        return await self._upsert(
            {
                "primary_id": media.primary_id,
                "primary_source": media.primary_source,
                "media_type": media.media_type,
            },
            update_doc,
            self._make_context(
                operation="upsert_media",
                external_id=media.primary_id,
                external_source=media.primary_source,
                media_type=media.media_type,
            ),
        )

    async def get_media_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
    ) -> Optional[MediaDB]:

        return await self._find_one(
            {
                "primary_id": external_id,
                "primary_source": external_source,
                "media_type": media_type,
            },
            self._make_context(
                operation="find_one_by_external_id_and_source_and_media_type",
                external_id=external_id,
                external_source=external_source,
                media_type=media_type,
            ),
        )

    async def update_media_scores_by_external_id_and_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        media_type: MediaType,
        scores: List[MediaScore],
    ) -> Optional[MediaDB]:
        context = DBOpContext(
            external_id=external_id,
            external_source=external_source,
            media_type=media_type,
            operation="update_scores",
            collection=self.collection.name,
        )
        data = {"scores": [score.model_dump() for score in scores]}

        async def _op():
            return await self.collection.find_one_and_update(
                {
                    "primary_id": external_id,
                    "primary_source": external_source,
                    "media_type": media_type,
                },
                {"$set": {**data, "updated_at": utc_now()}},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event="mongo_media_update_scores_query",
            error_event="mongo_media_update_scores_error",
            context=context,
        )

        return MediaDB.model_validate(doc) if doc else None

    async def delete_media_by_external_id_and_source_and_media_type(
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
                operation="delete_by_external_id_and_source_and_media_type",
                external_id=external_id,
                external_source=external_source,
                media_type=media_type,
            ),
        )
