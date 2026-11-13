from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings
from app.repositories.media.external_payload_repository import ExternalPayloadRepository
from app.repositories.media.media_core_repository import MediaCoreRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.repositories.user_repository import UserRepository


@dataclass
class Repositories:
    users: UserRepository
    user_media_entries: UserMediaEntryRepository
    reviews: ReviewRepository
    external_payload: ExternalPayloadRepository
    media_core: MediaCoreRepository


async def init_repositories(
    db: AsyncIOMotorDatabase,
    settings: Settings,
) -> Repositories:
    repositories = Repositories(
        users=UserRepository(db, settings.user_collection),
        user_media_entries=UserMediaEntryRepository(
            db, settings.user_media_entry_collection
        ),
        reviews=ReviewRepository(db, settings.review_collection),
        external_payload=ExternalPayloadRepository(
            db, settings.external_payload_collection
        ),
        media_core=MediaCoreRepository(db, settings.media_core_collection),
    )

    await repositories.users.init_indexes()
    await repositories.user_media_entries.init_indexes()
    await repositories.reviews.init_indexes()
    await repositories.media_core.init_indexes()
    return repositories
