from typing import List, Optional
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from pymongo.errors import PyMongoError
from bson import ObjectId
from app.models.review_models import ReviewDB, ReviewUpdate
from pydantic import ValidationError
import os
from dotenv import load_dotenv
import logging

load_dotenv()  # Load .env

# Setup logging
logger = logging.getLogger("reviews")
logging.basicConfig(level=logging.INFO)


class ReviewsCRUD:
    def __init__(self):
        mongodb_uri = os.getenv("MONGODB_URI")
        database_name = os.getenv("DATABASE_NAME")
        review_collection = os.getenv("REVIEW_COLLECTION")

        # Validate environment variables
        if not mongodb_uri:
            logger.error("MONGODB_URI environment variable is not set.")
            raise ValueError("MONGODB_URI environment variable is not set.")
        if not database_name:
            logger.error("DATABASE_NAME environment variable is not set.")
            raise ValueError("DATABASE_NAME environment variable is not set.")
        if not review_collection:
            logger.error("REVIEW_COLLECTION environment variable is not set.")
            raise ValueError("REVIEW_COLLECTION environment variable is not set.")

        try:
            self.client = MongoClient(mongodb_uri, server_api=ServerApi("1"))
            self.db = self.client[database_name]
            self.collection = self.db[review_collection]
            logger.info("MongoDB connection established.")
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def map_to_model(self, mongo_doc: dict) -> ReviewDB:
        mongo_doc["id"] = str(mongo_doc["_id"])
        mongo_doc.pop("_id", None)
        logger.debug(f"Mapping MongoDB doc to ReviewDB: {mongo_doc}")
        try:
            return ReviewDB(**mongo_doc)
        except ValidationError as e:
            logger.error(f"Pydantic validation error mapping doc to ReviewDB: {e}")
            raise

    def is_exists(self, review_id: str) -> bool:
        try:
            exists = self.collection.count_documents({"_id": ObjectId(review_id)}, limit=1) > 0
            logger.info(f"Review exists for id {review_id}: {exists}")
            return exists
        except PyMongoError as e:
            logger.error(f"MongoDB error checking existence for review id {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking existence for review id {review_id}: {e}")
            raise

    def create_review(self, review_data: ReviewDB) -> InsertOneResult:
        try:
            data = review_data.model_dump()
            data.pop("id", None)
            result = self.collection.insert_one(data)
            logger.info(f"Created review with id {result.inserted_id}")
            return result
        except PyMongoError as e:
            logger.error(f"MongoDB error creating review: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating review: {e}")
            raise

    def delete_review(self, review_id: str) -> DeleteResult:
        try:
            result = self.collection.delete_one({"_id": ObjectId(review_id)})
            logger.info(
                f"Deleted review with id {review_id}, deleted count: {result.deleted_count}"
            )
            return result
        except PyMongoError as e:
            logger.error(f"MongoDB error deleting review with id {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting review with id {review_id}: {e}")
            raise

    def update_review(self, review_update: ReviewUpdate) -> UpdateResult:
        try:
            data_dict = review_update.model_dump()
            review_id = data_dict.pop("id", None)

            update_data = {k: v for k, v in data_dict.items() if v is not None}
            result = self.collection.update_one({"_id": ObjectId(review_id)}, {"$set": update_data})
            logger.info(
                f"Updated review with id {review_id}, matched count: {result.matched_count}, modified count: {result.modified_count}"
            )

            return result

        except PyMongoError as e:
            logger.error(f"MongoDB error updating review: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating review: {e}")
            raise

    def get_reviews_by_user_media_entry_id(
        self, user_media_entry_id: str
    ) -> Optional[List[ReviewDB]]:
        try:
            cursor = self.collection.find({"user_media_entry_id": user_media_entry_id})
            results = [self.map_to_model(doc) for doc in cursor]
            logger.info(
                f"Fetched {len(results)} reviews for user_media_entry {user_media_entry_id}"
            )
            return results
        except PyMongoError as e:
            logger.error(
                f"MongoDB error getting reviews for user_media_entry {user_media_entry_id}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error getting reviews for user_media_entry {user_media_entry_id}: {e}"
            )
            raise

    def get_review_by_id(self, review_id: str) -> Optional[ReviewDB]:
        try:
            data = self.collection.find_one({"_id": ObjectId(review_id)})
            if data:
                logger.info(f"Found review with id {review_id} ")
                return self.map_to_model(data)
            logger.info(f"No review found with id {review_id}")
            return None
        except PyMongoError as e:
            logger.error(f"MongoDB error finding review by _id {review_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error finding review by _id {review_id}: {e}")
            raise

    def count_reviews_by_user_media_entry_id(self, user_media_entry_id: str) -> int:
        try:
            query = {"user_media_entry_id": user_media_entry_id}

            count = self.collection.count_documents(query)
            logger.info(f"Counted {count} reviews for user_media_entry_id {user_media_entry_id} ")
            return count
        except PyMongoError as e:
            logger.error(
                f"MongoDB error counting reviews for user_media_entry_id {user_media_entry_id}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error counting reviews for user_media_entry_id {user_media_entry_id}: {e}"
            )
            raise
