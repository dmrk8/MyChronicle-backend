from typing import Any, Optional

from app.core.event_bus import EventBus
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.user_media_entry_models import (
    UserMediaEntry,
    UserMediaEntryCreate,
    UserMediaEntryDB,
    UserMediaEntryInsert,
    UserMediaEntrySyncMetadata,
    UserMediaEntryUpdate,
    UserMediaEntryPagination,
)
from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.services.review_service import ReviewService
from app.enums.user_media_entry_enums import (
    MediaExternalSource,
    UserMediaEntrySortFields,
    UserMediaEntrySortOptions,
)

import structlog
import re

logger = structlog.get_logger().bind(service="UserMediaEntryService")


class UserMediaEntryService:
    def __init__(
        self,
        repository: UserMediaEntryRepository,
        review_service: ReviewService,
        event_bus: EventBus | None = None,
    ):
        self.repository = repository
        self.review_service = review_service
        self.event_bus = event_bus

        # Register handlers when service is created
        if self.event_bus:
            self.event_bus.subscribe("user.deleted", self.on_user_deleted)

    async def on_user_deleted(self, *, user_id: str, **_: object) -> None:
        """Handle user deletion cascade."""
        await self.delete_all_entries_for_user(user_id)

    async def create_entry(
        self, entry_request: UserMediaEntryCreate, user_id: str
    ) -> UserMediaEntry:

        entry_data = UserMediaEntryInsert(
            **entry_request.model_dump(),
            user_id=user_id,
        )
        res = await self.repository.create_entry(entry_data)
        logger.info("entry_created", entry_id=res.id, user_id=user_id)
        return UserMediaEntry.from_db(res)

    async def get_entry_by_id(self, entry_id: str, user_id: str) -> UserMediaEntry:
        res = await self._verify_ownership(entry_id, user_id)
        return UserMediaEntry.from_db(res)

    async def update_entry(
        self, entry_id: str, update_data: UserMediaEntryUpdate, user_id: str
    ) -> Optional[UserMediaEntry]:
        await self._verify_ownership(entry_id, user_id)

        updated_entry = await self.repository.update_entry(
            entry_id, user_id, update_data
        )
        if updated_entry is None:
            logger.error(
                "entry_update_failed_data_missing",
                entry_id=entry_id,
            )
            raise RuntimeError(
                "UserMediaEntry missing after update - data integrity issue"
            )

        return UserMediaEntry.from_db(updated_entry)

    async def delete_entry(self, entry_id: str, user_id: str) -> None:
        await self._verify_ownership(entry_id, user_id)
        await self.review_service.delete_reviews_for_user_media_entry(entry_id, user_id)
        deleted = await self.repository.delete_entry(entry_id, user_id)
        if not deleted:
            raise RuntimeError(
                f"Delete operation not acknowledged for entry {entry_id}"
            )
        logger.info("entry_deleted", entry_id=entry_id, user_id=user_id)

    async def get_entry_by_external_id_and_source(
        self, external_id: int, external_source: MediaExternalSource, user_id: str
    ) -> Optional[UserMediaEntry]:
        res = await self.repository.get_entry_by_external_id_and_external_source_and_user_id(
            external_id, external_source, user_id
        )
        if not res:
            raise NotFoundException(
                f"Entry not found for external_id={external_id}, source={external_source}"
            )

        return UserMediaEntry.from_db(res)

    async def get_entries(
        self,
        user_id: str,
        in_library: Optional[bool],
        is_favorite: Optional[bool],
        status: Optional[str],
        media_type: Optional[str],
        page: int,
        per_page: int,
        sort_by: UserMediaEntrySortFields,
        sort_order: UserMediaEntrySortOptions,
        title_search: Optional[str],
        is_adult: Optional[bool],
    ) -> UserMediaEntryPagination:
        filters: dict[str, Any] = {}

        if in_library is not None:
            filters["in_library"] = in_library
        if is_favorite is not None:
            filters["is_favorite"] = is_favorite
        if status is not None:
            filters["status"] = status
        if media_type is not None:
            filters["media_type"] = media_type
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

        entries = await self.repository.get_entries(
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            user_id=user_id,
        )
        total = await self.repository.count_entries(user_id=user_id, filters=filters)
        has_next_page = (page * per_page) < total
        return UserMediaEntryPagination(
            results=[UserMediaEntry.from_db(e) for e in entries],
            page=page,
            perPage=per_page,
            hasNextPage=has_next_page,
            total=total,
        )

    async def count_entries_by_user_id(self, user_id: str) -> int:
        count = await self.repository.count_entries_by_user_id(user_id)
        return count

    async def _verify_ownership(self, entry_id: str, user_id: str) -> UserMediaEntryDB:
        entry = await self.repository.get_entry_by_id(entry_id, user_id)
        if not entry:
            raise NotFoundException(f"Entry {entry_id} not found")
        if entry.user_id != user_id:
            logger.warning(
                "unauthorized_access_attempt", user_id=user_id, entry_id=entry_id
            )
            raise ForbiddenException("You do not have access to this entry")
        return entry

    async def sync_entry_metadata(
        self, entry_id: str, metadata: UserMediaEntrySyncMetadata, user_id: str
    ) -> Optional[UserMediaEntry]:
        """Sync metadata from external API"""
        await self._verify_ownership(entry_id, user_id)

        synced_entry = await self.repository.sync_entry_metadata(
            entry_id, user_id, metadata
        )
        if synced_entry is None:
            raise RuntimeError(
                "UserMediaEntry missing after metadata sync - data integrity issue"
            )
        logger.info("entry_synced", entry_id=entry_id)
        return UserMediaEntry.from_db(synced_entry)

    async def delete_all_entries_for_user(self, user_id: str) -> None:
        """Delete all media entries (and their reviews) for a user."""
        deleted = await self.repository.delete_by_user_id(user_id)
        if not deleted:
            raise RuntimeError(f"Failed to delete entries for user {user_id}")

        await self.review_service.delete_all_reviews_for_user(user_id)
        logger.info(
            "all_entries_deleted_for_user",
            user_id=user_id,
        )
