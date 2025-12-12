from fastapi import Depends
import os
from pymongo.database import Database
from app.core.database import get_database

from app.services.anilist_service import AnilistService
from app.integrations.anilistApi import AnilistApi

from app.services.tmdb_service import TMDBService
from app.integrations.tmdb_api import TMDBApi

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

def get_anilist_api() -> AnilistApi:
    return AnilistApi()

def get_anilist_service(anilist_api: AnilistApi = Depends(get_anilist_api)) -> AnilistService:
    return AnilistService(anilist_api=anilist_api)


def get_tmdb_api() -> TMDBApi:
    return TMDBApi()

def get_tmdb_service(tmdb_api: TMDBApi = Depends(get_tmdb_api)) -> TMDBService:
    return TMDBService(tmdb_api=tmdb_api)

def get_user_repository(db: Database = Depends(get_database)) -> UserRepository:
    collection_name = os.getenv("USER_COLLECTION_NAME", "users")  
    return UserRepository(db=db, collection_name=collection_name)

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository=user_repository)