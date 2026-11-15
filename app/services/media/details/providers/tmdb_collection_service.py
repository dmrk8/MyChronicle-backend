import asyncio
from datetime import timedelta

import structlog

from app.enums.media_enums import StoredDataType
from app.models.providers.tmdb_models import TMDBCollection
from app.services.media.storage.external_payload_service import ExternalPayloadService
from app.services.metadata.tmdb_service import TMDBService

logger = structlog.get_logger()


class TMDBCollectionService:
    def __init__(
        self,
        tmdb_service: TMDBService,
        external_payload_service: ExternalPayloadService,
    ):
        self.tmdb_service = tmdb_service
        self.external_payload_service = external_payload_service
        self.logger = logger.bind(service="TMDBCollectionService")

    async def get_collection_detail(
        self, collection_id: int
    ) -> TMDBCollection | None:
        cached = await self.external_payload_service.get(
            payload_type=StoredDataType.TMDB_COLLECTION,
            external_id=str(collection_id),
        )

        if cached:
            collection = self.external_payload_service.parse_as(
                cached, TMDBCollection
            )

            if collection and cached.is_fresh:
                return collection

            if collection:
                asyncio.create_task(self._refresh(collection_id))
                return collection

        return await self._refresh(collection_id)

    async def _refresh(self, collection_id: int) -> TMDBCollection | None:
        try:
            collection = await self.tmdb_service.get_collection_detail(collection_id)

            if not collection:
                return None

            await self.external_payload_service.save(
                payload_type=StoredDataType.TMDB_COLLECTION,
                external_id=str(collection_id),
                model=collection,
                ttl=timedelta(days=180),
            )

            return collection

        except Exception:
            self.logger.exception(
                "tmdb_collection_refresh_failed",
                collection_id=collection_id,
            )
            raise