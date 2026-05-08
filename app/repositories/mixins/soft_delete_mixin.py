from datetime import datetime

from app.models.db.db_context_model import DBOpContext
from app.utils.time_helpers import utc_now


class SoftDeleteMixin:
    """
    Mixin for repositories to add soft delete functionality.
    Requires the DBModel to have `is_deleted` (bool) and `deleted_at` (datetime) fields.
    Provides methods for soft deleting, restoring, and finding pending deletions.
    Requires the repository to inherit BaseRepository.
    """

    async def _soft_delete(self, query: dict, context: DBOpContext) -> bool:
        return bool(
            await self._update_one(  # type: ignore
                {**query, "is_deleted": False},
                {"is_deleted": True, "deleted_at": utc_now()},
                context,
            )
        )

    async def _restore(self, query: dict, context: DBOpContext) -> bool:
        return bool(
            await self._update_one(  # type: ignore
                {**query, "is_deleted": True},
                {"is_deleted": False, "deleted_at": None},
                context,
            )
        )

    async def _find_pending_deletion(
        self,
        before: datetime,
        context: DBOpContext,
        limit: int = 100,
    ):
        """For background worker: fetch soft-deleted docs older than `before`"""
        return await self._find_many(  # type: ignore
            query={"is_deleted": True, "deleted_at": {"$lt": before}},
            context=context,
            limit=limit,
        )
