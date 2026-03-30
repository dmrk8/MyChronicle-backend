from typing import Any, List, Optional
from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.services.review_service import ReviewService
from app.models.user_media_entry_models import (
    UserMediaEntryCreate,
    UserMediaEntryUpdate,
    UserMediaEntryDB,
    UserMediaEntryPagination,
)
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from datetime import datetime, timezone
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
        self, repository: UserMediaEntryRepository, review_service: ReviewService
    ):
        self.repository = repository
        self.review_service = review_service

    async def create_entry(
        self, entry_request: UserMediaEntryCreate, user_id: str
    ) -> UserMediaEntryDB:

        entry_data = UserMediaEntryDB(
            **entry_request.model_dump(),
            user_id=user_id,  # type: ignore
        )
        result: InsertOneResult = await self.repository.create_entry(entry_data)
        return await self.repository.get_entry_by_id(result.inserted_id)

    async def get_entry_by_id(self, entry_id: str, user_id: str) -> UserMediaEntryDB:
        return await self._verify_ownership(entry_id, user_id)

    async def update_entry(
        self, entry_id: str, update_data: UserMediaEntryUpdate, user_id: str
    ) -> UserMediaEntryDB:
        await self._verify_ownership(entry_id, user_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.now(timezone.utc)
        result: UpdateResult = await self.repository.update_entry(entry_id, update_dict)
        return await self.repository.get_entry_by_id(entry_id)

    async def delete_entry(self, entry_id: str, user_id: str) -> str:
        await self._verify_ownership(entry_id, user_id)
        await self.review_service.delete_reviews_by_user_media_entry_id(entry_id)
        result: DeleteResult = await self.repository.delete_entry(entry_id)
        if result.acknowledged:
            return entry_id
        else:
            raise ValueError("Failed to delete entry")

    async def get_entries_by_user_id(self, user_id: str) -> List[UserMediaEntryDB]:
        return await self.repository.get_entries_by_user_id(user_id)

    async def get_entry_by_external_id_and_source(
        self, external_id: int, external_source: MediaExternalSource, user_id: str
    ) -> Optional[UserMediaEntryDB]:
        return await self.repository.get_entry_by_external_id_and_external_source_and_user_id(
            external_id, external_source, user_id
        )

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
        filters: dict[str, Any] = {"user_id": user_id}

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
        )
        total = await self.repository.collection.count_documents(filters)
        has_next_page = (page * per_page) < total
        return UserMediaEntryPagination(
            results=entries,
            page=page,
            per_page=per_page,  # type: ignore
            has_next_page=has_next_page,  # type: ignore
            total=total,
        )

    async def count_entries_by_user_id(self, user_id: str) -> int:
        count = await self.repository.count_entries_by_user_id(user_id)
        return count

    async def _verify_ownership(self, entry_id: str, user_id: str) -> UserMediaEntryDB:
        entry = await self.repository.get_entry_by_id(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")
        if entry.user_id != user_id:
            logger.warning(
                "Unauthorized access attempt", user_id=user_id, entry_id=entry_id
            )
            raise ValueError("User not authorized for this entry")
        return entry
