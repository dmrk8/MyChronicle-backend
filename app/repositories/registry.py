from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings
from app.repositories.media.external_payload_repository import ExternalPayloadRepository
from app.repositories.media.media_core_repository import MediaCoreRepository


@dataclass
class Repositories:
    external_payload: ExternalPayloadRepository
    media_core: MediaCoreRepository


async def init_repositories(
    db: AsyncIOMotorDatabase,
    settings: Settings,
) -> Repositories:
    repositories = Repositories(
        external_payload=ExternalPayloadRepository(
            db, settings.external_payload_collection
        ),
        media_core=MediaCoreRepository(db, settings.media_core_collection),
    )

    await repositories.media_core.init_indexes()
    return repositories
