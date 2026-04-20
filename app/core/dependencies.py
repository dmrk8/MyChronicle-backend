from fastapi import Depends, Request
from redis.asyncio import Redis

from app.core.config import Settings, get_settings
from app.core.event_bus import EventBus
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.repositories import Repositories
from app.integrations.omdb_api import OMDbApi
from app.services.anilist_service import AnilistService
from app.integrations.anilist_api import AnilistApi

from app.services.external_storage_service import ExternalStorageService
from app.services.media_db_service import  MediaDatabaseService
from app.services.media_service import MediaService
from app.services.omdb_service import OMDbService
from app.services.redis_service import RedisService
from app.services.review_service import ReviewService
from app.services.sync_service import SyncService
from app.services.tmdb_service import TMDBService
from app.integrations.tmdb_api import TMDBApi

from app.services.user_service import UserService

from app.auth.jwt_handler import JWTHandler
from app.services.auth_service import AuthService
from app.auth.password_handler import PasswordHandler

from app.services.user_media_entry_service import UserMediaEntryService


def get_anilist_api(request: Request) -> AnilistApi:
    return AnilistApi(request.app.state.anilist_client)


def get_tmdb_api(
    request: Request, settings: Settings = Depends(get_settings)
) -> TMDBApi:
    return TMDBApi(settings.tmdb_access_token, request.app.state.tmdb_client)


def get_omdb_api(
    request: Request, settings: Settings = Depends(get_settings)
) -> OMDbApi:
    return OMDbApi(settings.omdb_api_key, request.app.state.omdb_client)


def get_password_handler(request: Request) -> PasswordHandler:
    return request.app.state.password_handler


def get_mongo(request: Request) -> AsyncIOMotorDatabase:
    settings = request.app.state.settings
    return request.app.state.mongo_client[settings.database_name]


def get_repositories(request: Request) -> Repositories:
    return request.app.state.repositories


def get_redis(request: Request) -> Redis:
    return request.app.state.redis_client


def get_redis_service(redis_client: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis_client=redis_client)


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


def get_anilist_service(
    anilist_api: AnilistApi = Depends(get_anilist_api),
) -> AnilistService:
    return AnilistService(anilist_api=anilist_api)


def get_tmdb_service(tmdb_api: TMDBApi = Depends(get_tmdb_api)) -> TMDBService:
    return TMDBService(tmdb_api=tmdb_api)


def get_jwt_handler(request: Request) -> JWTHandler:
    return request.app.state.jwt_handler


def get_user_service(
    repos: Repositories = Depends(get_repositories),
    password_handler: PasswordHandler = Depends(get_password_handler),
    event_bus: EventBus = Depends(get_event_bus),
) -> UserService:
    return UserService(
        user_repository=repos.user,
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


def get_review_service(
    repos: Repositories = Depends(get_repositories),
) -> ReviewService:
    return ReviewService(
        review_repository=repos.review,
        user_media_entry_repository=repos.user_media_entry,
    )


def get_user_media_entry_service(
    repos: Repositories = Depends(get_repositories),
    review_service: ReviewService = Depends(get_review_service),
    event_bus: EventBus = Depends(get_event_bus),
) -> UserMediaEntryService:
    return UserMediaEntryService(
        repository=repos.user_media_entry,
        review_service=review_service,
        event_bus=event_bus,
    )



def get_omdb_service(
    omdb_api: OMDbApi = Depends(get_omdb_api),
) -> OMDbService:
    return OMDbService(omdb_api=omdb_api)


def get_external_storage_service(
    repo: Repositories = Depends(get_repositories),
) -> ExternalStorageService:
    return ExternalStorageService(repository=repo.external_storage)


def get_media_database_service(
    repo: Repositories = Depends(get_repositories),
) -> MediaDatabaseService:
    return MediaDatabaseService(repository=repo.media)


def get_sync_service(
    media_database_service: MediaDatabaseService = Depends(get_media_database_service),
    anilist_service: AnilistService = Depends(get_anilist_service),
    tmdb_service: TMDBService = Depends(get_tmdb_service),
    omdb_service: OMDbService = Depends(get_omdb_service),
    external_storage_service: ExternalStorageService = Depends(
        get_external_storage_service
    ),
) -> SyncService:
    return SyncService(
        media_database_service=media_database_service,
        anilist_service=anilist_service,
        tmdb_service=tmdb_service,
        omdb_service=omdb_service,
        external_storage_service=external_storage_service,
    )


def get_media_service(
    redis_service: RedisService = Depends(get_redis_service),
    anilist_service: AnilistService = Depends(get_anilist_service),
    tmdb_service: TMDBService = Depends(get_tmdb_service),
    sync_service: SyncService = Depends(get_sync_service),
    external_storage_service: ExternalStorageService = Depends(
        get_external_storage_service
    ),
    media_database_service: MediaDatabaseService = Depends(get_media_database_service),
) -> MediaService:
    return MediaService(
        redis_service=redis_service,
        anilist_service=anilist_service,
        tmdb_service=tmdb_service,
        sync_service=sync_service,
        external_storage_service=external_storage_service,
        media_database_service=media_database_service,
    )
