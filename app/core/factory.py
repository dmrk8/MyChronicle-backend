from fastapi import FastAPI
from contextlib import asynccontextmanager
import structlog

from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from httpx import AsyncClient

from app.core.logging import setup_logging
from app.core.repositories import init_repositories
from app.core.event_bus import EventBus
from app.auth.password_handler import PasswordHandler
from app.auth.jwt_handler import JWTHandler

logger = structlog.get_logger()


def create_app(settings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("app_startup")

        app.state.settings = settings

        # logging
        setup_logging(settings)

        # Mongo
        app.state.mongo_client = AsyncIOMotorClient(
            settings.mongodb_uri,
            maxPoolSize=10,
            minPoolSize=2,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=5000,
        )
        await app.state.mongo_client.admin.command("ping")

        # Redis
        app.state.redis_client = Redis.from_url(
            settings.redis_url, decode_responses=True
        )
        await app.state.redis_client.ping()

        # HTTP clients
        app.state.anilist_client = AsyncClient(timeout=10.0)
        app.state.tmdb_client = AsyncClient(timeout=10.0)

        # Core services
        app.state.event_bus = EventBus()
        app.state.password_handler = PasswordHandler()
        app.state.jwt_handler = JWTHandler(
            secret=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            expire_days=settings.jwt_access_token_expire_days,
        )

        # Repositories
        db = app.state.mongo_client[settings.database_name]
        app.state.repos = await init_repositories(db, settings)

        yield

        logger.info("app_shutdown")

        app.state.mongo_client.close()
        await app.state.redis_client.close()
        await app.state.anilist_client.aclose()
        await app.state.tmdb_client.aclose()

    app = FastAPI(title=settings.service_name, lifespan=lifespan)

    # ------------------------
    # Middleware
    # ------------------------
    from app.middleware.request_context import RequestContextMiddleware
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------
    # Exception Handlers
    # ------------------------
    from app.core.exception_handlers import (
        app_exception_handler,
        unhandled_exception_handler,
    )
    from app.core.exceptions import AppException

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ------------------------
    # Routes
    # ------------------------
    @app.get("/health")
    async def health_check():
        logger.info("health check")
        return {
            "status": "healthy",
            "service": settings.service_name,
            "environment": settings.env,
        }

    from app.routes.auth_router import auth_router
    from app.routes.user_router import user_router
    from app.routes.imdb_router import imdb_router
    from app.routes.igdb_router import igdb_router
    from app.routes.anilist_router import anilist_router
    from app.routes.tmdb_router import tmdb_router
    from app.routes.user_media_entry_router import user_media_entry_router

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(imdb_router)
    app.include_router(igdb_router)
    app.include_router(anilist_router)
    app.include_router(tmdb_router)
    app.include_router(user_media_entry_router)

    return app
