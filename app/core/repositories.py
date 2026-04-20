from app.repositories.external_storage_repository import ExternalStorageRepository
from app.repositories.media_repository import MediaRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_media_entry_repository import UserMediaEntryRepository

class Repositories:
    def __init__(
        self,
        user_repo: UserRepository,
        user_media_entry_repo: UserMediaEntryRepository,
        review_repo: ReviewRepository,
        external_storage_repo: ExternalStorageRepository,
        media_repo: MediaRepository
    ):
        self.user = user_repo
        self.user_media_entry = user_media_entry_repo
        self.review = review_repo
        self.external_storage = external_storage_repo
        self.media = media_repo

    async def close(self):
        pass


async def init_repositories(db, settings) -> Repositories:
    user_repo = UserRepository(
        db=db,
        collection_name=settings.user_collection,
    )

    user_media_entry_repo = UserMediaEntryRepository(
        db=db,
        collection_name=settings.user_media_entry_collection,
    )

    review_repo = ReviewRepository(
        db=db,
        collection_name=settings.review_collection,
    )
    external_storage_repo = ExternalStorageRepository(
        db=db,
        collection_name=settings.external_storage_collection,
    )
    media_repo = MediaRepository(
        db=db,
        collection_name=settings.media_core_collection,
    )


    await user_repo.init_indexes()
    await user_media_entry_repo.init_indexes()
    await external_storage_repo.init_indexes()
    await media_repo.init_indexes()

    return Repositories(
        user_repo=user_repo,
        user_media_entry_repo=user_media_entry_repo,
        review_repo=review_repo,
        external_storage_repo=external_storage_repo,
        media_repo=media_repo,
    )
