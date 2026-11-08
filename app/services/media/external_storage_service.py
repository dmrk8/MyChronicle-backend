from datetime import timedelta

from typing import Optional, TypeVar

from pydantic import BaseModel, ValidationError
import structlog

from app.enums.media_enums import (
    StoredDataType,
)
from app.models.db.external_storage_models import (
    ExternalDataDB,
    ExternalDataUpsert,
)
from app.repositories.media.external_storage_repository import ExternalStorageRepository
from app.utils.time_helpers import utc_now

T = TypeVar("T", bound=BaseModel)

logger = structlog.get_logger()


class ExternalStorageService:
    def __init__(
        self,
        repository: ExternalStorageRepository,
    ):
        self.repository = repository
        self.logger = logger.bind(service="ExternalStorageService")

    def parse_as(self, doc: ExternalDataDB, model: type[T]) -> T | None:
        """Parse an ExternalDataDB into a Pydantic model.

        Args:
            doc (ExternalDataDB): The document to parse.
            model (type[T]): The Pydantic model to parse the document into.

        Returns:
            T | None: The parsed Pydantic model, or None if parsing fails.
        """
        try:
            return model.model_validate(doc.payload)
        except ValidationError as e:
            self.logger.warning(
                "cache_parse_failed", payload_type=doc.payload_type.value, error=str(e)
            )
            return None

    async def get(
        self,
        payload_type: StoredDataType,
        external_id: str,
    ) -> Optional[ExternalDataDB]:
        return await self.repository.get(payload_type, external_id)

    async def delete(
        self,
        payload_type: StoredDataType,
        external_id: str,
    ) -> bool:
        return await self.repository.delete(payload_type, external_id)

    async def save(
        self,
        payload_type: StoredDataType,
        external_id: str,
        model: BaseModel,
        ttl: timedelta | None,
    ) -> ExternalDataDB:
        """Save a Pydantic model to the external storage.

        Args:
            payload_type (StoredDataType): The type of the payload.
            external_id (str): The external ID of the payload.
            model (BaseModel): The Pydantic model to save.
            ttl (timedelta | None): The time-to-live for the payload.

        Returns:
            ExternalDataDB: The saved ExternalDataDB instance.
        """

        expires_at = utc_now() + ttl if ttl else None
        payload = model.model_dump(mode="json", by_alias=True)
        upsert_model = ExternalDataUpsert(
            external_id=external_id,
            payload_type=payload_type,
            payload=payload,
            expires_at=expires_at,
        )

        return await self.repository.upsert(upsert_model)
