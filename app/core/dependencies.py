from fastapi import Depends

from app.core.config import Settings, get_settings

from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_db

from app.services.anilist_service import AnilistService
from app.integrations.anilistApi import AnilistApi

from app.services.tmdb_service import TMDBService
from app.integrations.tmdb_api import TMDBApi

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

from app.auth.jwt_handler import JWTHandler
from app.services.auth_service import AuthService
from app.auth.password_handler import PasswordHandler


def get_anilist_api() -> AnilistApi:
    return AnilistApi()


def get_anilist_service(anilist_api: AnilistApi = Depends(get_anilist_api)) -> AnilistService:
    return AnilistService(anilist_api=anilist_api)


def get_tmdb_api(settings: Settings = Depends(get_settings)) -> TMDBApi:
    return TMDBApi(settings.tmdb_access_token)


def get_tmdb_service(tmdb_api: TMDBApi = Depends(get_tmdb_api)) -> TMDBService:
    return TMDBService(tmdb_api=tmdb_api)


def get_user_repository(
    db: AsyncIOMotorDatabase = Depends(get_db), settings: Settings = Depends(get_settings)
) -> UserRepository:
    collection_name = settings.user_collection
    return UserRepository(db=db, collection_name=collection_name)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_handler: PasswordHandler = Depends(PasswordHandler),
) -> UserService:
    return UserService(user_repository=user_repository, password_handler=password_handler)


def get_jwt_handler(settings: Settings = Depends(get_settings)) -> JWTHandler:
    return JWTHandler(
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        expire_minutes=settings.jwt_expire_minutes
    )


def get_auth_service(
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(jwt_handler=jwt_handler, user_service=user_service)


def get_password_handler() -> PasswordHandler:
    return PasswordHandler()
