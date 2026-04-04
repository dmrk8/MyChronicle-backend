import asyncio
from pathlib import Path
import sys
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings


async def migrate():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]

    reviews_col = db[settings.review_collection]
    entries_col = db[settings.user_media_entry_collection]

    reviews_missing_user_id = reviews_col.find({"user_id": {"$exists": False}})

    updated = 0
    failed = 0

    async for review in reviews_missing_user_id:
        raw_entry_id = review["user_media_entry_id"]

        try:
            entry_lookup_id = ObjectId(raw_entry_id)
        except Exception:
            entry_lookup_id = raw_entry_id

        entry = await entries_col.find_one({"_id": entry_lookup_id}, {"user_id": 1})

        if not entry:
            print(f"[WARN] No entry found for review {review['_id']}, skipping")
            failed += 1
            continue

        await reviews_col.update_one(
            {"_id": review["_id"]}, {"$set": {"user_id": entry["user_id"]}}
        )
        updated += 1

    print(f"Migration complete — updated: {updated}, failed: {failed}")
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
