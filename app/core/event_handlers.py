from app.core.event_bus import EventBus
from app.services.user_media_entry_service import UserMediaEntryService
import structlog

logger = structlog.get_logger()


def register_event_handlers(
    event_bus: EventBus,
    user_media_entry_service: UserMediaEntryService,
) -> None:

    async def on_user_deleted(*, user_id: str, **_: object) -> None:
        """Handle user deletion cascade - delete all user data across services."""
        logger.info("user_deleted_event_received", user_id=user_id)

        await user_media_entry_service.delete_all_entries_for_user(user_id)

        logger.info("user_deletion_cascade_completed", user_id=user_id)

    event_bus.subscribe("user.deleted", on_user_deleted)

    logger.info("event_handlers_registered")
