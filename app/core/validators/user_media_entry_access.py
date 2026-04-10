from app.core.exceptions import NotFoundException
from app.models.user_media_entry_models import UserMediaEntry
from app.repositories.user_media_entry_repository import UserMediaEntryRepository


class UserMediaEntryAccessValidator:
    def __init__(self, entry_repository: UserMediaEntryRepository):
        self.entry_repository = entry_repository

    async def verify(self, entry_id: str, user_id: str) -> UserMediaEntry:
        entry = await self.entry_repository.get_entry_by_id(entry_id, user_id)

        if not entry:
            raise NotFoundException(f"Entry {entry_id} not found")

        return UserMediaEntry.from_db(entry)
