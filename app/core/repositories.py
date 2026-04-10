import asyncio

from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_media_entry_repository import UserMediaEntryRepository


class Repositories:
    def __init__(self, user_repo, user_media_entry_repo, review_repo):
        self.user = user_repo
        self.user_media_entry = user_media_entry_repo
        self.review = review_repo


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

    await asyncio.gather(
        user_repo.init_indexes(),
        user_media_entry_repo.init_indexes(),
    )

    return Repositories(
        user_repo=user_repo,
        user_media_entry_repo=user_media_entry_repo,
        review_repo=review_repo,
    )
