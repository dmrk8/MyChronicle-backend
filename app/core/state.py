from dataclasses import dataclass

from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from app.core.config import Settings
from app.repositories.registry import Repositories


@dataclass
class AppState:
    settings: Settings
    mongo_client: AsyncIOMotorClient
    redis_client: Redis
    anilist_client: AsyncClient
    tmdb_client: AsyncClient
    omdb_client: AsyncClient
    mal_client: AsyncClient
    repositories: Repositories
