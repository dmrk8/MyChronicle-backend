from typing import Any
from unittest.mock import MagicMock
from motor.motor_asyncio import AsyncIOMotorClient

import pytest

from app.core import dependencies as deps
from app.integrations.anilistApi import AnilistApi
from app.integrations.tmdb_api import TMDBApi
from app.repositories.user_repository import UserRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_media_entry_repository import UserMediaEntryRepository
from app.services.user_service import UserService
from app.services.review_service import ReviewService
from app.auth.jwt_handler import JWTHandler
from app.auth.password_handler import PasswordHandler
from motor.motor_asyncio import AsyncIOMotorClient


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


@pytest.fixture(autouse=True)
def reset_dependency_singletons():
    deps._anilist_api = None
    deps._tmdb_api = None
    deps._password_handler = None
    deps._jwt_handler = None

    deps.state.anilist_client = None
    deps.state.tmdb_client = None
    deps.state.mongo_client = None

    yield

    deps._anilist_api = None
    deps._tmdb_api = None
    deps._password_handler = None
    deps._jwt_handler = None


def test_get_anilist_api_caches_instance():
    client = MagicMock()
    deps.state.anilist_client = client

    first = deps.get_anilist_api()
    second = deps.get_anilist_api()

    assert first is second
    assert first.client is client


def test_get_tmdb_api_caches_instance_from_settings():
    client = MagicMock()
    settings = create_mock_settings(tmdb_access_token="abc123")
    deps.state.tmdb_client = client

    first = deps.get_tmdb_api(settings=settings)
    second = deps.get_tmdb_api(settings=settings)

    assert first is second
    assert first.client is client
    assert first.tmdb_access_token == "abc123"


def test_get_password_handler_caches_instance():
    first = deps.get_password_handler()
    second = deps.get_password_handler()

    assert first is second


def test_get_mongo_uses_database_name_from_settings(monkeypatch):
    database = MagicMock()
    db = create_mock_motor_client()
    db.__getitem__.return_value = database

    settings = create_mock_settings(database_name="otakutime")
    monkeypatch.setattr(deps, "get_settings", lambda: settings)

    deps.state.mongo_client = db  
    resolved = deps.get_mongo()

    assert resolved is database


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

    deps.state.mongo_client = db  
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


def test_get_jwt_handler_caches_first_instance():
    first = deps.get_jwt_handler(settings=create_mock_settings(jwt_secret_key="first"))
    second = deps.get_jwt_handler(
        settings=create_mock_settings(jwt_secret_key="second")
    )

    assert first is second
    assert first.secret_key == "first"


def test_get_user_service_wires_dependencies():
    repository = MagicMock(spec=UserRepository)
    password_handler = MagicMock(spec=PasswordHandler)

    service = deps.get_user_service(
        user_repository=repository,
        password_handler=password_handler,
    )

    assert service.user_repository is repository
    assert service.password_handler is password_handler


def test_get_auth_service_wires_dependencies():
    jwt_handler = MagicMock(spec=JWTHandler)
    user_service = MagicMock(spec=UserService)

    service = deps.get_auth_service(
        jwt_handler=jwt_handler,
        user_service=user_service,
    )

    assert service.jwt_handler is jwt_handler
    assert service.user_service is user_service


def test_get_review_service_wires_dependencies():
    review_repository = MagicMock(spec=ReviewRepository)

    service = deps.get_review_service(
        review_repository=review_repository,
    )

    assert service.review_repository is review_repository


def test_get_user_media_entry_service_wires_dependencies():
    repository = MagicMock(spec=UserMediaEntryRepository)
    review_service = MagicMock(spec=ReviewService)

    service = deps.get_user_media_entry_service(
        repository=repository,
        review_service=review_service,
    )

    assert service.repository is repository
    assert service.review_service is review_service
