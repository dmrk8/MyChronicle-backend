from fastapi import Depends, Request
from redis.asyncio import Redis

from app.core.config import Settings, get_settings
from app.core.event_bus import EventBus
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.anilist_service import AnilistService
from app.integrations.anilistApi import AnilistApi

from app.services.redis_service import RedisService
from app.services.review_service import ReviewService
from app.services.tmdb_service import TMDBService
from app.integrations.tmdb_api import TMDBApi

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

from app.auth.jwt_handler import JWTHandler
from app.services.auth_service import AuthService
from app.auth.password_handler import PasswordHandler

from app.repositories.review_repository import ReviewRepository

from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.services.user_media_entry_service import UserMediaEntryService


def get_anilist_api(request: Request) -> AnilistApi:
    return AnilistApi(request.app.state.anilist_client)


def get_tmdb_api(
    request: Request, settings: Settings = Depends(get_settings)
) -> TMDBApi:
    return TMDBApi(settings.tmdb_access_token, request.app.state.tmdb_client)


def get_password_handler(request: Request) -> PasswordHandler:
    return request.app.state.password_handler


def get_mongo(request: Request) -> AsyncIOMotorDatabase:
    settings = get_settings()
    return request.app.state.mongo_client[settings.database_name]


def get_redis(request: Request) -> Redis:
    return request.app.state.redis_client


def get_redis_service(redis_client: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis_client=redis_client)


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


def get_anilist_service(
    anilist_api: AnilistApi = Depends(get_anilist_api),
    redis_service: RedisService = Depends(get_redis_service),
) -> AnilistService:
    return AnilistService(anilist_api=anilist_api, redis_service=redis_service)


def get_tmdb_service(tmdb_api: TMDBApi = Depends(get_tmdb_api)) -> TMDBService:
    return TMDBService(tmdb_api=tmdb_api)


def get_user_repository(
    db: AsyncIOMotorDatabase = Depends(get_mongo),
    settings: Settings = Depends(get_settings),
) -> UserRepository:
    collection_name = settings.user_collection
    return UserRepository(db=db, collection_name=collection_name)


def get_jwt_handler(request: Request) -> JWTHandler:
    return request.app.state.jwt_handler


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_handler: PasswordHandler = Depends(get_password_handler),
    event_bus: EventBus = Depends(get_event_bus),
) -> UserService:
    return UserService(
        user_repository=user_repository,
        password_handler=password_handler,
        event_bus=event_bus,
    )


def get_auth_service(
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(
        jwt_handler=jwt_handler,
        user_service=user_service,
    )


def get_review_repository(
    db: AsyncIOMotorDatabase = Depends(get_mongo),
    settings: Settings = Depends(get_settings),
) -> ReviewRepository:
    return ReviewRepository(db=db, collection_name=settings.review_collection)


def get_user_media_entry_repository(
    db: AsyncIOMotorDatabase = Depends(get_mongo),
    settings: Settings = Depends(get_settings),
) -> UserMediaEntryRepository:
    return UserMediaEntryRepository(
        db=db, collection_name=settings.user_media_entry_collection
    )


def get_review_service(
    review_repository: ReviewRepository = Depends(get_review_repository),
    user_media_entry_repository: UserMediaEntryRepository = Depends(
        get_user_media_entry_repository
    ),
) -> ReviewService:
    return ReviewService(
        review_repository=review_repository,
        user_media_entry_repository=user_media_entry_repository,
    )


def get_user_media_entry_service(
    repository: UserMediaEntryRepository = Depends(get_user_media_entry_repository),
    review_service: ReviewService = Depends(get_review_service),
    event_bus: EventBus = Depends(get_event_bus),
) -> UserMediaEntryService:
    return UserMediaEntryService(
        repository=repository,
        review_service=review_service,
        event_bus=event_bus,
    )

