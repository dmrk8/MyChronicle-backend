import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings, get_settings
from contextlib import asynccontextmanager
from redis.asyncio import Redis

logger = logging.getLogger("mongo_client")
logging.basicConfig(level=logging.INFO)


class AppState:
    settings: Settings | None = None
    mongo_client: AsyncIOMotorClient | None = None
    redis_client: Redis | None = None


state = AppState()


@asynccontextmanager
async def lifespan(app):
    logger.info("loading_configuration")
    logger.info("connecting_to_databases")

    try:
        state.settings = get_settings()
        
    except Exception as e:
        raise  # Stop startup if config is invalid

    state.mongo_client = AsyncIOMotorClient(
        state.settings.mongodb_uri, maxPoolSize=10, minPoolSize=2
    )
    logger.info("mongodb_connected")

    state.redis_client = Redis(
        host=state.settings.redis_host,
        port=state.settings.redis_port,
        username=state.settings.redis_username,
        password=state.settings.redis_password,
        decode_responses=True,
        max_connections=10,
    )
    await state.redis_client.ping()  # Test connection
    logger.info("redis_connected")

    yield

    logger.info("closing_connections")
    if state.mongo_client:
        state.mongo_client.close()
    if state.redis_client:
        await state.redis_client.close()
    logger.info("connections_closed")
