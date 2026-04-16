from dataclasses import dataclass

from app.models.db.user_media_entry_models import UserMediaEntry
from app.models.db.user_models import User


@dataclass
class UserMediaEntryContext:
    entry_id: str
    user: User
    entry: UserMediaEntry

