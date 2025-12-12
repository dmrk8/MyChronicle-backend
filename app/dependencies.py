from fastapi import Depends
from app.services.anilist_service import AnilistService
from app.integrations.anilistApi import AnilistApi

from app.services.tmdb_service import TMDBService
from app.integrations.tmdb_api import TMDBApi


def get_anilist_api() -> AnilistApi:
    return AnilistApi()

def get_anilist_service(anilist_api: AnilistApi = Depends(get_anilist_api)) -> AnilistService:
    return AnilistService(anilist_api=anilist_api)


def get_tmdb_api() -> TMDBApi:
    return TMDBApi()

def get_tmdb_service(tmdb_api: TMDBApi = Depends(TMDBApi)) -> TMDBService:
    return TMDBService(tmdb_api=tmdb_api) 