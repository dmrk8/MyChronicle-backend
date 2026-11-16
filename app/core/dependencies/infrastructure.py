"""Application state, persistence, cache, and external API dependencies."""

from fastapi import Depends, Request
from redis.asyncio import Redis

from app.core.state import AppState
from app.integrations.anilist_api import AnilistApi
from app.integrations.mal_api import MALApi
from app.integrations.omdb_api import OMDbApi
from app.integrations.tmdb_api import TMDBApi
from app.repositories.registry import Repositories


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state


def get_repositories(state: AppState = Depends(get_app_state)) -> Repositories:
    return state.repositories


def get_redis(state: AppState = Depends(get_app_state)) -> Redis:
    return state.redis_client


def get_anilist_api(state: AppState = Depends(get_app_state)) -> AnilistApi:
    return AnilistApi(state.anilist_client)


def get_tmdb_api(state: AppState = Depends(get_app_state)) -> TMDBApi:
    return TMDBApi(state.settings.tmdb_access_token, state.tmdb_client)


def get_omdb_api(state: AppState = Depends(get_app_state)) -> OMDbApi:
    return OMDbApi(state.settings.omdb_api_key, state.omdb_client)


def get_mal_api(state: AppState = Depends(get_app_state)) -> MALApi:
    return MALApi(state.settings.mal_client_id, state.mal_client)
