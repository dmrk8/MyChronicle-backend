import structlog
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings, get_settings
from app.core.logging import setup_logging
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from httpx import AsyncClient

logger = structlog.get_logger()


class AppState:
    settings: Settings | None = None
    mongo_client: AsyncIOMotorClient | None = None
    redis_client: Redis | None = None
    anilist_client: AsyncClient | None = None
    tmdb_client: AsyncClient | None = None


state = AppState()


@asynccontextmanager
async def lifespan(app):
    logger.info("loading_configuration")

    try:
        state.settings = get_settings()

    except Exception:
        logger.critical("failed_to_load_settings", exc_info=True)
        raise

    setup_logging(state.settings)
    logger.info("logging_initialized", env=state.settings.env)

    logger.info("connecting_to_mongodb")
    try:
        state.mongo_client = AsyncIOMotorClient(
            state.settings.mongodb_uri,
            maxPoolSize=10,
            minPoolSize=2,
        )
        logger.info("mongodb_connected")
    except Exception:
        logger.critical("mongodb_connection_failed", exc_info=True)
        raise

    # logger.info("connecting_to_redis")
    # try:
    #     state.redis_client = Redis(
    #         host=state.settings.redis_host,
    #         port=state.settings.redis_port,
    #         username=state.settings.redis_username,
    #         password=state.settings.redis_password,
    #         decode_responses=True,
    #         max_connections=10,
    #     )
    #     await state.redis_client.ping()
    #     logger.info("redis_connected")
    # except Exception:
    #     logger.critical("redis_connection_failed", exc_info=True)
    #     raise

    logger.info("opening httpx connections")
    state.anilist_client = AsyncClient(timeout=10.0)
    state.tmdb_client = AsyncClient(timeout=10.0)

    yield

    logger.info("closing_connections")
    if state.mongo_client:
        state.mongo_client.close()
    if state.redis_client:
        await state.redis_client.close()
    if state.anilist_client:
        await state.anilist_client.aclose()
    if state.tmdb_client:
        await state.tmdb_client.aclose()
    logger.info("connections_closed")
