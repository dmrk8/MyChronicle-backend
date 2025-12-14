import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError

logger = logging.getLogger("mongo_client")
logging.basicConfig(level=logging.INFO)

def create_mongo_client(mongodb_uri=None):
    if not mongodb_uri:
        mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise ValueError("MONGODB_URI is required")
    
    try:
        client = AsyncIOMotorClient(mongodb_uri, server_api=ServerApi("1"))
        logger.info("MongoDB connection successful")
        return client
    except PyMongoError as e:
        logger.error(f"MongoDB connection error: {e}")
        raise

def get_database(client, db_name=None) -> AsyncIOMotorDatabase:
    if not db_name:
        db_name = os.getenv("DATABASE_NAME")
    if not db_name:
        raise ValueError("DATABASE_NAME is required")
    return client[db_name]

def get_db() -> AsyncIOMotorDatabase:
    client = create_mongo_client()
    return get_database(client=client)