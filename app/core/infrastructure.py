from redis.asyncio import Redis
import structlog
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings
from app.core.logging import setup_logging
from contextlib import asynccontextmanager
from httpx import AsyncClient

from app.core.repositories import init_repositories
from app.core.event_bus import EventBus
from app.auth.password_handler import PasswordHandler
from app.auth.jwt_handler import JWTHandler

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app):
    logger.info("loading_configuration")

    try:
        app.state.settings = get_settings()

    except Exception:
        logger.critical("failed_to_load_settings", exc_info=True)
        raise

    setup_logging(app.state.settings)
    logger.info("logging_initialized", env=app.state.settings.env)

    logger.info("connecting_to_mongodb")
    try:
        app.state.mongo_client = AsyncIOMotorClient(
            app.state.settings.mongodb_uri,
            maxPoolSize=10,
            minPoolSize=2,
        )
        await app.state.mongo_client.admin.command("ping")
        logger.info("mongodb_connected")
    except Exception:
        logger.critical("mongodb_connection_failed", exc_info=True)
        raise

    logger.info("connecting_to_redis")
    try:
        app.state.redis_client = Redis.from_url(
            app.state.settings.redis_url, decode_responses=True
        )

        await app.state.redis_client.ping()
        logger.info("redis_connected")
    except Exception:
        logger.critical("redis_connection_failed", exc_info=True)
        raise

    logger.info("opening httpx connections")
    app.state.anilist_client = AsyncClient(timeout=10.0)
    app.state.tmdb_client = AsyncClient(timeout=10.0)

    app.state.event_bus = EventBus()

    # Initialize cached instances
    app.state.password_handler = PasswordHandler()
    app.state.jwt_handler = JWTHandler(
        secret=app.state.settings.jwt_secret_key,
        algorithm=app.state.settings.jwt_algorithm,
        issuer=app.state.settings.jwt_issuer,
        audience=app.state.settings.jwt_audience,
        expire_days=app.state.settings.jwt_access_token_expire_days,
    )

    db = app.state.mongo_client[app.state.settings.database_name]
    app.state.repos = await init_repositories(db, app.state.settings)

    yield

    logger.info("closing_connections")
    if app.state.mongo_client:
        app.state.mongo_client.close()
    if app.state.redis_client:
        await app.state.redis_client.close()
    if app.state.anilist_client:
        await app.state.anilist_client.aclose()
    if app.state.tmdb_client:
        await app.state.tmdb_client.aclose()
    logger.info("connections_closed")
