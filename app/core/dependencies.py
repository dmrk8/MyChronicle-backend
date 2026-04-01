from fastapi import Depends
from redis.asyncio import Redis

from app.core.config import Settings, get_settings
from app.core.infrastructure import state

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.anilist_service import AnilistService
from app.integrations.anilistApi import AnilistApi

from app.services.redis_service import RedisService
from app.services.tmdb_service import TMDBService
from app.integrations.tmdb_api import TMDBApi

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

from app.auth.jwt_handler import JWTHandler
from app.services.auth_service import AuthService
from app.auth.password_handler import PasswordHandler

from app.repositories.review_repository import ReviewRepository
from app.services.review_service import ReviewService

from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.services.user_media_entry_service import UserMediaEntryService

_anilist_api = None
_tmdb_api = None
_password_handler = None
_jwt_handler = None


def get_anilist_api() -> AnilistApi:
    global _anilist_api
    if _anilist_api is None:
        _anilist_api = AnilistApi(state.anilist_client)  # type: ignore
    return _anilist_api


def get_tmdb_api(settings: Settings = Depends(get_settings)) -> TMDBApi:
    global _tmdb_api
    if _tmdb_api is None:
        _tmdb_api = TMDBApi(settings.tmdb_access_token, state.tmdb_client)  # type: ignore
    return _tmdb_api


def get_password_handler() -> PasswordHandler:
    global _password_handler
    if _password_handler is None:
        _password_handler = PasswordHandler()
    return _password_handler


def get_mongo() -> AsyncIOMotorDatabase:
    settings = get_settings()
    return state.mongo_client[settings.database_name]  # type: ignore


def get_redis() -> Redis:
    return state.redis_client  # type: ignore


def get_redis_service(redis_client: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis_client=redis_client)


def get_anilist_service(
    anilist_api: AnilistApi = Depends(get_anilist_api),
   
) -> AnilistService:
    return AnilistService(anilist_api=anilist_api)


def get_tmdb_service(tmdb_api: TMDBApi = Depends(get_tmdb_api)) -> TMDBService:
    return TMDBService(tmdb_api=tmdb_api)


def get_user_repository(
    db: AsyncIOMotorDatabase = Depends(get_mongo),
    settings: Settings = Depends(get_settings),
) -> UserRepository:
    collection_name = settings.user_collection
    return UserRepository(db=db, collection_name=collection_name)


def get_jwt_handler(
    settings: Settings = Depends(get_settings)
) -> JWTHandler:
    global _jwt_handler
    if _jwt_handler is None:
        _jwt_handler = JWTHandler(
            secret=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            expire_days=settings.jwt_access_token_expire_days,
        )
    return _jwt_handler


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_handler: PasswordHandler = Depends(get_password_handler),
) -> UserService:
    return UserService(
        user_repository=user_repository, password_handler=password_handler
    )


def get_auth_service(
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    user_service: UserService = Depends(get_user_service)
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
) -> UserMediaEntryService:
    return UserMediaEntryService(repository=repository, review_service=review_service)
