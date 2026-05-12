from typing import Any, Optional
from pymongo.errors import DuplicateKeyError
from app.core.exceptions import ConflictException, NotFoundException
from app.enums.media_enums import MediaExternalSource, MediaType
from app.models.db.user_media_entry_models import (
    UserMediaEntryDB,
    UserMediaEntryCreate,
    UserMediaEntryDB,
    UserMediaEntryInsert,
    UserMediaEntrySyncMetadata,
    UserMediaEntryUpdate,
)
from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.enums.user_media_entry_enums import (
    UserMediaEntrySortFields,
    UserMediaEntrySortOptions,
    UserMediaEntryStatus,
)

import structlog
import re

logger = structlog.get_logger()


class UserMediaEntryService:
    def __init__(
        self,
        repository: UserMediaEntryRepository,
    ):
        self.repository = repository
        self.logger = logger.bind(service="UserMediaEntryService")

    async def _verify_ownership(self, entry_id: str, user_id: str) -> UserMediaEntryDB:
        """Verify ownership of the user media entry and return the document after

        Args:
            entry_id (str): ID of the user media entry
            user_id (str): ID of the user

        Raises:
            NotFoundException: If the entry does not exist or does not belong to the user

        Returns:
            UserMediaEntryDB: The verified user media entry
        """
        entry = await self.repository.get_entry_by_id_and_user_id(entry_id, user_id)
        if not entry:
            raise NotFoundException("Entry not found")
        return entry

    async def create_entry(
        self, entry_request: UserMediaEntryCreate, user_id: str
    ) -> UserMediaEntryDB:

        entry_data = UserMediaEntryInsert(
            **entry_request.model_dump(),
            user_id=user_id,
        )
        try:
            res = await self.repository.insert_entry(entry_data)
        except DuplicateKeyError:
            raise ConflictException("Entry is existing already in the library")
        self.logger.info("entry_created", entry_id=res.id, user_id=user_id)
        return res

    async def get_entry_by_id(self, entry_id: str, user_id: str) -> UserMediaEntryDB:
        return await self._verify_ownership(entry_id, user_id)

    async def update_entry(
        self,
        entry_id: str,
        update_data: UserMediaEntryUpdate,
        user_id: str,
    ) -> UserMediaEntryDB:
        await self._verify_ownership(entry_id, user_id)

        updated_entry = await self.repository.update_entry(
            entry_id, user_id, update_data
        )
        if updated_entry is None:
            raise NotFoundException("Entry Not Found")
        self.logger.info("entry_updated", entry_id=entry_id, user_id=user_id)

        return updated_entry

    async def delete_entry(self, entry_id: str, user_id: str) -> None:
        await self._verify_ownership(entry_id, user_id)
        await self.repository.soft_delete_by_id(entry_id, user_id)

        self.logger.info("entry_soft_deleted", entry_id=entry_id)

    async def get_entry_by_external_id_and_external_source_and_media_type(
        self,
        external_id: int,
        external_source: MediaExternalSource,
        user_id: str,
        media_type: MediaType,
    ) -> UserMediaEntryDB:
        res = await self.repository.get_entry_by_external_id_and_external_source_and_user_id_and_media_type(
            external_id, external_source, user_id, media_type.value
        )
        if not res:
            raise NotFoundException("Entry not found")

        return res

    async def get_entries_by_filters(
        self,
        user_id: str,
        in_library: Optional[bool],
        is_favorite: Optional[bool],
        status: Optional[UserMediaEntryStatus],
        media_type: Optional[MediaType],
        page: int,
        per_page: int,
        sort_by: UserMediaEntrySortFields,
        sort_order: UserMediaEntrySortOptions,
        title_search: Optional[str],
        is_adult: Optional[bool],
    ) -> tuple[list[UserMediaEntryDB], int, int, bool, int]:
        filters: dict[str, Any] = {}

        if in_library is not None:
            filters["in_library"] = in_library
        if is_favorite is not None:
            filters["is_favorite"] = is_favorite
        if status is not None:
            filters["status"] = status.value
        if media_type is not None:
            filters["media_type"] = media_type.value
        if title_search is not None:
            filters["title"] = {"$regex": re.escape(title_search), "$options": "i"}
        if is_adult is True:
            filters["is_adult"] = True
        elif is_adult is False:
            filters["$or"] = [
                {"is_adult": False},
                {"is_adult": {"$exists": False}},
                {"is_adult": None},
            ]

        entries = await self.repository.get_entries_with_filters(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by.value,
            sort_order=sort_order.value,
            user_id=user_id,
        )
        total = await self.repository.count_entries_with_filters(
            user_id=user_id, filters=filters
        )
        has_next_page = (page * per_page) < total

        return entries, page, per_page, has_next_page, total

    async def count_entries_for_user(self, user_id: str) -> int:
        count = await self.repository.count_entries_by_user_id(user_id)
        return count

    async def delete_all_entries_for_user(self, user_id: str) -> None:
        """Delete all media entries (and their reviews) for a user."""
        await self.repository.soft_delete_many_by_user_id(user_id)

        self.logger.info("all_entries_soft_deleted_for_user", user_id=user_id)

    async def sync_entry_metadata(
        self, entry_id: str, metadata: UserMediaEntrySyncMetadata, user_id: str
    ) -> UserMediaEntryDB:
        """Sync metadata from external API"""
        await self._verify_ownership(entry_id, user_id)

        synced_entry = await self.repository.sync_entry_metadata(
            entry_id, user_id, metadata
        )
        if synced_entry is None:
            raise NotFoundException("Entry Not Found")
        return synced_entry
