from fastapi import Depends
from app.services.anilist_service import AnilistService
from app.integrations.anilistApi import AnilistApi

def get_anilist_api() -> AnilistApi:
    return AnilistApi()

def get_anilist_service(anilist_api: AnilistApi = Depends(get_anilist_api)) -> AnilistService:
    return AnilistService(anilist_api=anilist_api)


