import logging
from typing import Optional
from bson import ObjectId
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from pymongo.errors import PyMongoError
from pymongo.database import Database
from app.models.user_models import UserDB, UserUpdate

logger = logging.getLogger("user_repository")
logging.basicConfig(level=logging.INFO)


class UserRepository:
    def __init__(self, db: Database, collection_name: str):
        self.db = db
        self.collection = db[collection_name]

    def map_to_model(self, mongo_doc: dict) -> UserDB:
        mongo_doc["id"] = str(mongo_doc["_id"])
        mongo_doc.pop("_id", None)
        return UserDB(**mongo_doc)

    def create(self, user: UserDB) -> InsertOneResult:
        try:
            data = user.model_dump()
            data.pop("id", None)

            result = self.collection.insert_one(data)
            logger.info(f"User created with id {result.inserted_id}")
            return result

        except PyMongoError as e:
            logger.error(f"MongoDB error creating user: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            raise

    def update(self, user_update: UserUpdate) -> UpdateResult:
        try:
            data_dict = user_update.model_dump()
            user_id = data_dict.pop("id", None)

            update_data = {k: v for k, v in data_dict.items() if v is not None}

            result = self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
            logger.info(
                f"Updated user with id {user_id}, matched count: {result.matched_count}, modified count: {result.modified_count}"
            )
            return result
        except PyMongoError as e:
            logger.error(f"MongoDB error updating user: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating user: {e}")
            raise

    def delete(self, user_id: str) -> DeleteResult:
        try:
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            logger.info(f"Deleted user with id {user_id}, deleted count: {result.deleted_count}")
            return result

        except PyMongoError as e:
            logger.error(f"MongoDB error deleting user: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting user: {e}")
            raise

    def get_by_id(self, id: str) -> Optional[UserDB]:
        try:
            user_doc = self.collection.find_one({"_id": ObjectId(id)})

            if user_doc:
                logger.info(f"Found user with id {id}")
                return self.map_to_model(user_doc)
            logger.info(f"No user found with id {id}")
            return None

        except PyMongoError as e:
            logger.error(f"MongoDB error getting user by id {id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting user by id {id}: {e}")
            raise

    def is_username_exists(self, username: str) -> bool:
        try:
            user_doc = self.collection.find_one({"username": username})
            exists = user_doc is not None
            logger.info(f"Username {username} exists: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"MongoDB error checking username existence: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking username existence: {e}")
            raise

    def get_by_username(self, username: str) -> Optional[UserDB]:
        try:
            user_doc = self.collection.find_one({"username": username})

            if user_doc:
                logger.info(f"Found user with username {username}")
                return self.map_to_model(user_doc)
            logger.info(f"No user found with username {username}")
            return None

        except PyMongoError as e:
            logger.error(f"MongoDB error finding user by username {username}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error finding user by username {username}: {e}")
            raise
