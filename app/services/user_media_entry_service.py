from typing import Any, List, Optional
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.review_models import Review, ReviewCreate, ReviewInsert, ReviewUpdate
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.models.user_media_entry_models import (
    UserMediaEntry,
    UserMediaEntryCreate,
    UserMediaEntryInsert,
    UserMediaEntryUpdate,
    UserMediaEntryPagination,
)
from pymongo.results import DeleteResult
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
        self, repository: UserMediaEntryRepository, review_repository: ReviewRepository
    ):
        self.repository = repository
        self.review_repository = review_repository

    async def create_entry(
        self, entry_request: UserMediaEntryCreate, user_id: str
    ) -> UserMediaEntry:

        entry_data = UserMediaEntryInsert(
            **entry_request.model_dump(),
            user_id=user_id,
        )
        res = await self.repository.create_entry(entry_data)
        return UserMediaEntry.from_db(res)

    async def get_entry_by_id(self, entry_id: str, user_id: str) -> UserMediaEntry:
        return await self._verify_ownership(entry_id, user_id)

    async def update_entry(
        self, entry_id: str, update_data: UserMediaEntryUpdate, user_id: str
    ) -> Optional[UserMediaEntry]:
        await self._verify_ownership(entry_id, user_id)

        updated_entry = await self.repository.update_entry(
            entry_id, user_id, update_data
        )
        if updated_entry is None:
            raise RuntimeError(
                "UserMediaEntry missing after update - data integrity issue"
            )

        return UserMediaEntry.from_db(updated_entry)

    async def delete_entry(self, entry_id: str, user_id: str) -> None:
        await self._verify_ownership(entry_id, user_id)
        await self.review_repository.delete_reviews_by_user_media_entry_id(
            entry_id, user_id
        )
        result: DeleteResult = await self.repository.delete_entry(entry_id, user_id)
        if not result.acknowledged:
            raise RuntimeError(
                f"Delete operation not acknowledged for entry {entry_id}"
            )

    async def get_entry_by_external_id_and_source(
        self, external_id: int, external_source: MediaExternalSource, user_id: str
    ) -> Optional[UserMediaEntry]:
        res = await self.repository.get_entry_by_external_id_and_external_source_and_user_id(
            external_id, external_source, user_id
        )
        if res:
            return UserMediaEntry.from_db(res)
        return None

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

    async def _verify_ownership(self, entry_id: str, user_id: str) -> UserMediaEntry:
        entry = await self.repository.get_entry_by_id(entry_id, user_id)
        if not entry:
            raise NotFoundException(f"Entry {entry_id} not found")
        if entry.user_id != user_id:
            logger.warning(
                "unauthorized_access_attempt", user_id=user_id, entry_id=entry_id
            )
            raise ForbiddenException("You do not have access to this entry")
        return UserMediaEntry.from_db(entry)

    async def create_review(
        self, review_request: ReviewCreate, entry_id: str, user_id: str
    ) -> Review:
        review_data = ReviewInsert(
            **review_request.model_dump(), user_id=user_id, user_media_entry_id=entry_id
        )
        result = await self.review_repository.create_review(review_data)

        logger.info(
            "review_created",
            user_media_entry_id=entry_id,
            review_id=result.id,
            user_id=user_id,
        )
        return Review.from_db(result)

    async def update_review(
        self, review_id: str, entry_id: str, update_request: ReviewUpdate, user_id: str
    ) -> Optional[Review]:
        await self._verify_ownership(entry_id, user_id)

        updated_review = await self.review_repository.update_review(
            review_id, update_request, user_id
        )

        if updated_review is None:
            raise RuntimeError("Review missing after update - data integrity issue")

        logger.info("review_updated", review_id=review_id, user_id=user_id)
        return Review.from_db(updated_review)

    async def delete_review(self, entry_id: str, review_id: str, user_id: str) -> None:
        await self._verify_ownership(entry_id, user_id)

        result: DeleteResult = await self.review_repository.delete_review(
            review_id, user_id
        )
        if not result.acknowledged:
            raise RuntimeError(f"Failed to delete review {review_id}")

        logger.info("review_deleted", review_id=review_id, user_id=user_id)

    async def get_reviews_for_user_media_entry(
        self, entry_id: str, user_id: str
    ) -> Optional[List[Review]]:
        await self._verify_ownership(entry_id, user_id)

        reviews = (
            await self.review_repository.get_reviews_by_user_media_entry_id_and_user_id(
                entry_id, user_id
            )
        )
        logger.info(
            "reviews_fetched",
            user_media_entry_id=entry_id,
            user_id=user_id,
        )
        if not reviews:
            return None

        return [Review.from_db(review) for review in reviews]

    async def get_review_by_id(
        self, review_id: str, user_id: str, entry_id: str
    ) -> Review:

        await self._verify_ownership(entry_id, user_id)
        try:
            res = await self.review_repository.get_review_by_id(
                review_id, user_id, entry_id
            )
            if res is None:
                raise NotFoundException(f"Review {review_id} not found")
            return Review.from_db(res)
        except Exception:
            raise NotFoundException(f"Review {review_id} not found")

    async def count_reviews_for_user_media_entry(
        self, user_media_entry_id: str, user_id: str
    ) -> int:
        return await self.review_repository.count_reviews_by_user_media_entry_id(
            user_media_entry_id, user_id
        )

    async def delete_reviews_for_user_media_entry(
        self, user_media_entry_id: str, user_id: str
    ) -> None:
        result: DeleteResult = (
            await self.review_repository.delete_reviews_by_user_media_entry_id(
                user_media_entry_id, user_id
            )
        )
        if not result.acknowledged:
            raise RuntimeError(
                f"Failed to delete reviews for entry id: {user_media_entry_id}"
            )
        logger.info(
            "reviews_deleted",
            user_media_entry_id=user_media_entry_id,
            user_id=user_id,
            deleted_count=result.deleted_count,
        )

    async def delete_all_reviews_for_user(self, user_id: str) -> None:
        result: DeleteResult = await self.review_repository.delete_by_user_id(user_id)
        if not result.acknowledged:
            raise RuntimeError(
                f"Deleting all reviews for user is not acknowledged {user_id}"
            )

        logger.info(
            "reviews_deleted_by_user",
            user_id=user_id,
            deleted_count=result.deleted_count,
        )
