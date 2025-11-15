from typing import List, Optional
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from app.models.review_models import ReviewDB, ReviewResponse
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
        
        self.client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        self.db = self.client[database_name]
        self.collection = self.db[review_collection]
        logger.info("MongoDB connection established.")

    def map_to_model(self, mongo_doc : dict) -> ReviewDB:
        mongo_doc["id"] = str(mongo_doc["_id"])
        mongo_doc.pop("_id", None)
        logger.debug(f"Mapping MongoDB doc to ReviewDB: {mongo_doc}")
        return ReviewDB(**mongo_doc)
    
    def create_review(self, review_data : ReviewDB) -> ReviewResponse:
        try:
            data = review_data.model_dump()
            data.pop("id", None)
            result = self.collection.insert_one(data)
            logger.info(f"Created review with id {result.inserted_id}")
            return ReviewResponse(
                message="Review created successfully", # type: ignore
                review_id=str(result.inserted_id), # type: ignore
                acknowledged=result.acknowledged # type: ignore
            )
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            raise
    
    def delete_review(self, review_id: str) -> ReviewResponse:
        try:
            result = self.collection.delete_one({"_id": ObjectId(review_id)})
            logger.info(f"Deleted review with id {review_id}, deleted count: {result.deleted_count}")
            return ReviewResponse(
                message="Review deleted", # type: ignore
                review_id=review_id, # type: ignore
                deleted_count=result.deleted_count, # type: ignore
                acknowledged=result.acknowledged # type: ignore
            )
        except Exception as e:
            logger.error(f"Error handling deleting review in repo: {e}")
            raise
        
    def update_review(self, updated_data : ReviewDB) -> ReviewResponse:
        try:
            data_dict = updated_data.model_dump()
            review_id = data_dict.pop("id", None)
            if not review_id:
                logger.error("Cannot update review without an id")
                raise ValueError("Cannot update review without an id")
            result = self.collection.update_one(
                {"_id": ObjectId(review_id)},
                {"$set": data_dict}
            )
            logger.info(f"Updated review with id {review_id}, matched count: {result.matched_count}, modified count: {result.modified_count}")
            
            return ReviewResponse(
                message="Review updated",
                review_id=review_id, # type: ignore
                matched_count=result.matched_count, # type: ignore
                modified_count=result.modified_count, # type: ignore
                acknowledged=result.acknowledged,
                updated_at=updated_data.updated_at # type: ignore
            ) 
            
        except Exception as e:
            logger.error(f"Error updating review: {e}")
            raise  
          
    def get_reviews_by_userid(self, user_id : str) -> List[ReviewDB]:
        try:
            cursor = self.collection.find({"user_id": user_id})
            results = [self.map_to_model(doc) for doc in cursor]
            logger.info(f"Fetched {len(results)} reviews for user {user_id}")
            return results
        except Exception as e:
            logger.error(f"Error getting reviews for user {user_id}: {e}")
            raise

    def get_review_by_id_and_user_id(self, review_id: str, user_id: str) -> Optional[ReviewDB]:
        try:
            data = self.collection.find_one({"_id": ObjectId(review_id), "user_id": user_id})
            if data:
                logger.info(f"Found review with id {review_id} for user {user_id}")
                return self.map_to_model(data)
            logger.info(f"No review found with id {review_id} for user {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error finding review by _id {review_id} for user {user_id}: {e}")
            raise

    def get_review_by_user_and_media(self, user_id: str, media_id: int):
        try:
            data = self.collection.find_one({"user_id": user_id, "media_id": media_id})
            if data:
                logger.info(f"Found review for user {user_id} and media {media_id}")
                return self.map_to_model(data)
            logger.info(f"No review found for user {user_id} and media {media_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting review by user id and media id: {e}")
            raise
        
    def get_review_id_by_media_id(self, user_id: str, media_id: int) -> Optional[str]:
        try:
            data = self.collection.find_one({"user_id": user_id, "media_id": media_id}, {"_id": 1})
            if data and "_id" in data:
                logger.info(f"Found review ID for user {user_id} and media {media_id}")
                return str(data["_id"])
            logger.info(f"No review ID found for user {user_id} and media {media_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting review ID by user id and media id: {e}")
            raise    

    def get_reviews(self, user_id: str,
                    filters: dict,
                    page: int,
                    per_page: int,
                    sort_by: str,
                    sort_order: int) -> List[ReviewDB]: 
        try:
            query = {"user_id": user_id}
            if filters: 
                query.update(filters) 
            skip = (page - 1) * per_page
            cursor = self.collection.find(query).sort(sort_by, sort_order).skip(skip).limit(per_page)
            results = [self.map_to_model(doc) for doc in cursor]
            logger.info(f"Fetched {len(results)} reviews for user {user_id} with filters {filters} on page {page}")
            return results
        except Exception as e:
            logger.error(f"Error getting reviews in filtered and sorted for user {user_id}: {e}")
            raise

    def count_reviews_by_user(self, user_id: str, filters: dict) -> int:
        try:
            query = {"user_id": user_id}
            if filters:
                query.update(filters) 
            count = self.collection.count_documents(query)
            logger.info(f"Counted {count} reviews for user {user_id} with filters {filters}")
            return count
        except Exception as e:
            logger.error(f"Error counting reviews {user_id}: {e}")
            raise








