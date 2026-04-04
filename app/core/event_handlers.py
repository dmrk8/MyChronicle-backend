from datetime import datetime
from app.core.event_bus import EventBus
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_media_entry_repository import UserMediaEntryRepository
import structlog

logger = structlog.get_logger()


def register_event_handlers(
    event_bus: EventBus,
    review_repo: ReviewRepository,
    user_media_entry_repo: UserMediaEntryRepository,
) -> None:

    async def on_review_changed(
        *,
        user_media_entry_id: str,
        occurred_at: datetime,
        **_: object,
    ) -> None:
        await user_media_entry_repo.update_entry(
            user_media_entry_id,
            {"updated_at": occurred_at},
        )

    event_bus.subscribe("review.changed", on_review_changed)

    logger.info("event_handlers_registered")
