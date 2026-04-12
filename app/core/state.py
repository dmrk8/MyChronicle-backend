from typing import Optional

from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from redis import Redis

from app.auth.jwt_handler import JWTHandler
from app.auth.password_handler import PasswordHandler
from app.core.config import Settings
from app.core.event_bus import EventBus


class AppState(BaseModel):
    """
    Documentation class for app.state attributes.

    This class documents the structure of app.state but is not directly assigned to it.
    FastAPI uses Starlette's native State object, but this class serves as a reference
    for IDE autocomplete and type checking.
    """

    class Config:
        arbitrary_types_allowed = True

    settings: Optional[Settings] = None
    mongo_client: Optional[AsyncIOMotorClient] = None
    redis_client: Optional[Redis] = None
    anilist_client: Optional[AsyncClient] = None
    tmdb_client: Optional[AsyncClient] = None
    event_bus: Optional[EventBus] = None
    password_handler: Optional[PasswordHandler] = None
    jwt_handler: Optional[JWTHandler] = None
    repos: Optional[dict] = None
