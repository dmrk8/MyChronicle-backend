from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core import infrastructure as infra
from app.core.event_bus import EventBus
from app.auth.password_handler import PasswordHandler
from app.auth.jwt_handler import JWTHandler


class FakeMongoClient:
    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        self.closed = False
        self.databases = {}

    def __getitem__(self, name):
        if name not in self.databases:
            self.databases[name] = MagicMock(name=f"db:{name}")
        return self.databases[name]

    def close(self):
        self.closed = True


class FakeAsyncClient:
    instances = []

    def __init__(self, timeout):
        self.timeout = timeout
        self.closed = False
        FakeAsyncClient.instances.append(self)

    async def aclose(self):
        self.closed = True


@pytest.fixture
def mock_app():
    """Create a mock app with state object."""
    app = MagicMock()
    app.state = MagicMock()
    return app


@pytest.fixture
def reset_fake_clients():
    FakeAsyncClient.instances = []
    yield
    FakeAsyncClient.instances = []


@pytest.mark.asyncio
async def test_lifespan_initializes_and_closes_clients(
    monkeypatch, mock_app, reset_fake_clients
):
    settings = SimpleNamespace(
        env="test",
        mongodb_uri="mongodb://localhost:27017",
        database_name="testdb",
        review_collection="reviews",
        user_media_entry_collection="user_media_entries",
        jwt_secret_key="test-secret",
        jwt_algorithm="HS256",
        jwt_issuer="test",
        jwt_audience="test",
        jwt_access_token_expire_days=7,
    )
    setup_calls = []
    mock_repos = MagicMock()
    init_repos_calls = []

    async def mock_init_repositories(db, settings):
        init_repos_calls.append((db, settings))
        return mock_repos

    monkeypatch.setattr(infra, "get_settings", lambda: settings)
    monkeypatch.setattr(infra, "setup_logging", lambda s: setup_calls.append(s))
    monkeypatch.setattr(infra, "AsyncIOMotorClient", FakeMongoClient)
    monkeypatch.setattr(infra, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(infra, "init_repositories", mock_init_repositories)

    async with infra.lifespan(mock_app):
        assert mock_app.state.settings is settings
        assert isinstance(mock_app.state.mongo_client, FakeMongoClient)
        assert mock_app.state.mongo_client.uri == settings.mongodb_uri
        assert mock_app.state.mongo_client.kwargs == {
            "maxPoolSize": 10,
            "minPoolSize": 2,
        }

        assert len(FakeAsyncClient.instances) == 2
        assert all(client.timeout == 10.0 for client in FakeAsyncClient.instances)
        assert setup_calls == [settings]

        assert len(init_repos_calls) == 1
        assert mock_app.state.repos is mock_repos

        # Verify event_bus was initialized
        assert isinstance(mock_app.state.event_bus, EventBus)

        # Verify password_handler was initialized
        assert isinstance(mock_app.state.password_handler, PasswordHandler)

        # Verify jwt_handler was initialized with correct parameters
        assert isinstance(mock_app.state.jwt_handler, JWTHandler)
        assert mock_app.state.jwt_handler.secret_key == settings.jwt_secret_key
        assert mock_app.state.jwt_handler.algorithm == settings.jwt_algorithm
        assert mock_app.state.jwt_handler.issuer == settings.jwt_issuer
        assert mock_app.state.jwt_handler.audience == settings.jwt_audience

    assert mock_app.state.mongo_client.closed is True
    assert all(client.closed is True for client in FakeAsyncClient.instances)


@pytest.mark.asyncio
async def test_lifespan_raises_when_settings_fail(monkeypatch, mock_app):
    monkeypatch.setattr(
        infra,
        "get_settings",
        lambda: (_ for _ in ()).throw(RuntimeError("settings error")),
    )

    with pytest.raises(RuntimeError, match="settings error"):
        async with infra.lifespan(mock_app):
            pass


@pytest.mark.asyncio
async def test_lifespan_raises_when_mongodb_connection_fails(monkeypatch, mock_app):
    settings = SimpleNamespace(env="test", mongodb_uri="mongodb://localhost:27017")

    def raise_mongo(*args, **kwargs):
        raise RuntimeError("mongo error")

    monkeypatch.setattr(infra, "get_settings", lambda: settings)
    monkeypatch.setattr(infra, "setup_logging", lambda _: None)
    monkeypatch.setattr(infra, "AsyncIOMotorClient", raise_mongo)

    with pytest.raises(RuntimeError, match="mongo error"):
        async with infra.lifespan(mock_app):
            pass
