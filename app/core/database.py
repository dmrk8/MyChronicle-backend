import logging
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError
from app.core.config import Settings, get_settings

logger = logging.getLogger("mongo_client")
logging.basicConfig(level=logging.INFO)

def create_mongo_client(settings: Settings) -> AsyncIOMotorClient:
    mongodb_uri = settings.mongodb_uri
    if not mongodb_uri:
        raise ValueError("MONGODB_URI is required")
    
    try:
        client = AsyncIOMotorClient(mongodb_uri, server_api=ServerApi("1"))
        logger.info("MongoDB connection successful")
        return client
    except PyMongoError as e:
        logger.error(f"MongoDB connection error: {e}")
        raise

def get_database(client: AsyncIOMotorClient, settings: Settings) -> AsyncIOMotorDatabase:
    db_name = settings.database_name
    if not db_name:
        raise ValueError("DATABASE_NAME is required")
    return client[db_name]

def get_db(settings: Settings = Depends(get_settings)) -> AsyncIOMotorDatabase:
    client = create_mongo_client(settings)
    return get_database(client, settings)