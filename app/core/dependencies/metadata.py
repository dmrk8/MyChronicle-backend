from fastapi import Depends

from app.core.dependencies.infrastructure import (
    get_anilist_api,
    get_mal_api,
    get_omdb_api,
    get_tmdb_api,
)
from app.integrations.anilist_api import AnilistApi
from app.integrations.mal_api import MALApi
from app.integrations.omdb_api import OMDbApi
from app.integrations.tmdb_api import TMDBApi
from app.services.metadata.anilist_service import AnilistService
from app.services.metadata.mal_service import MALService
from app.services.metadata.omdb_service import OMDbService
from app.services.metadata.tmdb_service import TMDBService


def get_anilist_service(
    anilist_api: AnilistApi = Depends(get_anilist_api),
) -> AnilistService:
    return AnilistService(anilist_api=anilist_api)


def get_tmdb_service(
    tmdb_api: TMDBApi = Depends(get_tmdb_api),
) -> TMDBService:
    return TMDBService(tmdb_api=tmdb_api)


def get_omdb_service(
    omdb_api: OMDbApi = Depends(get_omdb_api),
) -> OMDbService:
    return OMDbService(omdb_api=omdb_api)

def get_mal_service(
    mal_api: MALApi = Depends(get_mal_api),
) -> MALService:
    return MALService(mal_api=mal_api)
