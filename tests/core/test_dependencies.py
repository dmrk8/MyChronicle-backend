from typing import Any
from unittest.mock import MagicMock
from motor.motor_asyncio import AsyncIOMotorClient

import pytest

from app.core import dependencies as deps
from app.core.event_bus import EventBus
from app.integrations.anilistApi import AnilistApi
from app.integrations.tmdb_api import TMDBApi
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.auth.jwt_handler import JWTHandler
from app.auth.password_handler import PasswordHandler


def create_mock_motor_client() -> Any:
    """Create a mock that satisfies AsyncIOMotorClient type."""
    mock = MagicMock(spec=AsyncIOMotorClient)
    mock.__getitem__ = MagicMock(return_value=MagicMock())
    return mock


def create_mock_settings(**overrides: Any) -> Any:
    """Create a Settings mock with required attributes."""
    settings = MagicMock()
    settings.tmdb_access_token = overrides.get("tmdb_access_token", "tmdb-token")
    settings.database_name = overrides.get("database_name", "otakutime")
    settings.user_collection = overrides.get("user_collection", "users")
    settings.review_collection = overrides.get("review_collection", "reviews")
    settings.user_media_entry_collection = overrides.get(
        "user_media_entry_collection", "entries"
    )
    settings.jwt_secret_key = overrides.get("jwt_secret_key", "super-secret")
    settings.jwt_algorithm = overrides.get("jwt_algorithm", "HS256")
    settings.jwt_issuer = overrides.get("jwt_issuer", "otakutime")
    settings.jwt_audience = overrides.get("jwt_audience", "otakutime-users")
    settings.jwt_access_token_expire_minutes = overrides.get(
        "jwt_access_token_expire_minutes", 15
    )
    settings.jwt_refresh_token_expire_days_default = overrides.get(
        "jwt_refresh_token_expire_days_default", 30
    )
    return settings


@pytest.fixture
def mock_request():
    """Create a mock request with app.state."""
    request = MagicMock()
    request.app = MagicMock()
    request.app.state = MagicMock()
    return request


def test_get_anilist_api_returns_instance(mock_request):
    client = MagicMock()
    mock_request.app.state.anilist_client = client

    result = deps.get_anilist_api(request=mock_request)

    assert isinstance(result, AnilistApi)
    assert result.client is client


def test_get_tmdb_api_returns_instance(mock_request):
    client = MagicMock()
    settings = create_mock_settings(tmdb_access_token="abc123")
    mock_request.app.state.tmdb_client = client

    result = deps.get_tmdb_api(request=mock_request, settings=settings)

    assert isinstance(result, TMDBApi)
    assert result.client is client
    assert result.tmdb_access_token == "abc123"


def test_get_password_handler_returns_instance(mock_request):
    password_handler = MagicMock(spec=PasswordHandler)
    mock_request.app.state.password_handler = password_handler

    result = deps.get_password_handler(request=mock_request)

    assert result is password_handler


def test_get_mongo_uses_database_name_from_settings(mock_request, monkeypatch):
    database = MagicMock()
    db = create_mock_motor_client()
    db.__getitem__ = MagicMock(return_value=database)

    settings = create_mock_settings(database_name="otakutime")
    mock_request.app.state.mongo_client = db
    monkeypatch.setattr(deps, "get_settings", lambda: settings)

    resolved = deps.get_mongo(request=mock_request)

    assert resolved is database
    db.__getitem__.assert_called_with("otakutime")


def test_get_anilist_service_wires_api():
    api = MagicMock(spec=AnilistApi)

    service = deps.get_anilist_service(anilist_api=api)

    assert service.anilist_api is api


def test_get_tmdb_service_wires_api():
    api = MagicMock(spec=TMDBApi)

    service = deps.get_tmdb_service(tmdb_api=api)

    assert service.tmdb_api is api


def test_get_user_repository_uses_user_collection():
    users_collection = MagicMock()
    db = create_mock_motor_client()
    db.__getitem__.return_value = users_collection

    repository = deps.get_user_repository(
        db=db, settings=create_mock_settings(user_collection="users")
    )

    assert repository.collection is users_collection


def test_get_review_repository_uses_review_collection():
    reviews_collection = MagicMock()
    db = create_mock_motor_client()
    db.__getitem__.return_value = reviews_collection

    repository = deps.get_review_repository(
        db=db,
        settings=create_mock_settings(review_collection="reviews"),
    )

    assert repository.collection is reviews_collection


def test_get_user_media_entry_repository_uses_configured_collection():
    entries_collection = MagicMock()
    db = create_mock_motor_client()
    db.__getitem__.return_value = entries_collection

    repository = deps.get_user_media_entry_repository(
        db=db,
        settings=create_mock_settings(user_media_entry_collection="entries"),
    )

    assert repository.collection is entries_collection


def test_get_jwt_handler_returns_from_state(mock_request):
    jwt_handler = MagicMock(spec=JWTHandler)
    mock_request.app.state.jwt_handler = jwt_handler

    result = deps.get_jwt_handler(request=mock_request)

    assert result is jwt_handler


def test_get_user_service_wires_dependencies():
    repository = MagicMock(spec=UserRepository)
    password_handler = MagicMock(spec=PasswordHandler)
    event_bus = MagicMock(spec=EventBus)

    service = deps.get_user_service(
        user_repository=repository,
        password_handler=password_handler,
        event_bus=event_bus,
    )

    assert service.user_repository is repository
    assert service.password_handler is password_handler
    assert service.event_bus is event_bus


def test_get_auth_service_wires_dependencies():
    jwt_handler = MagicMock(spec=JWTHandler)
    user_service = MagicMock(spec=UserService)

    service = deps.get_auth_service(
        jwt_handler=jwt_handler,
        user_service=user_service,
    )

    assert service.jwt_handler is jwt_handler
    assert service.user_service is user_service
