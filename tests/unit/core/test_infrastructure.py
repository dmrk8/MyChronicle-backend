from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core import infrastructure as infra
from app.core.event_bus import EventBus
from app.auth.password_handler import PasswordHandler
from app.auth.jwt_handler import JWTHandler


class FakeMongoAdmin:
    """Fake MongoDB admin object for ping command."""

    async def command(self, command_name):
        if command_name == "ping":
            return {"ok": 1.0}
        raise ValueError(f"Unknown command: {command_name}")


class FakeMongoClient:
    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        self.closed = False
        self.databases = {}
        self.admin = FakeMongoAdmin()

    def __getitem__(self, name):
        if name not in self.databases:
            self.databases[name] = MagicMock(name=f"db:{name}")
        return self.databases[name]

    def close(self):
        self.closed = True


class FakeRedis:
    instances = []

    def __init__(self, url, **kwargs):
        self.url = url
        self.kwargs = kwargs
        self.closed = False
        FakeRedis.instances.append(self)

    @classmethod
    def from_url(cls, url, **kwargs):
        """Create FakeRedis instance from URL."""
        return cls(url, **kwargs)

    async def ping(self):
        """Mock ping command."""
        return True

    async def close(self):
        """Mock close method."""
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
    FakeRedis.instances = []
    yield
    FakeAsyncClient.instances = []
    FakeRedis.instances = []


@pytest.mark.asyncio
async def test_lifespan_initializes_and_closes_clients(
    monkeypatch, mock_app, reset_fake_clients
):
    settings = SimpleNamespace(
        env="test",
        mongodb_uri="mongodb://localhost:27017",
        database_name="testdb",
        review_collection="reviews",
        user_collection="users",
        user_media_entry_collection="user_media_entries",
        redis_url="redis://localhost:6379/0",
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
    monkeypatch.setattr(infra, "Redis", FakeRedis)
    monkeypatch.setattr(infra, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(infra, "init_repositories", mock_init_repositories)

    async with infra.lifespan(mock_app):
        # Verify settings
        assert mock_app.state.settings is settings

        # Verify MongoDB client
        assert isinstance(mock_app.state.mongo_client, FakeMongoClient)
        assert mock_app.state.mongo_client.uri == settings.mongodb_uri
        assert mock_app.state.mongo_client.kwargs == {
            "maxPoolSize": 10,
            "minPoolSize": 2,
            "serverSelectionTimeoutMS": 3000,
            "connectTimeoutMS": 3000,
            "socketTimeoutMS": 5000,
        }

        # Verify Redis client
        assert isinstance(mock_app.state.redis_client, FakeRedis)
        assert mock_app.state.redis_client.url == settings.redis_url
        assert mock_app.state.redis_client.kwargs == {"decode_responses": True}
        assert len(FakeRedis.instances) == 1

        # Verify HTTP clients
        assert len(FakeAsyncClient.instances) == 2
        assert all(client.timeout == 10.0 for client in FakeAsyncClient.instances)

        # Verify setup and repositories
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

    # Verify cleanup
    assert mock_app.state.mongo_client.closed is True
    assert mock_app.state.redis_client.closed is True
    assert all(client.closed is True for client in FakeAsyncClient.instances)


@pytest.mark.asyncio
async def test_lifespan_raises_when_settings_fail(monkeypatch, mock_app):
    """Test that lifespan raises when settings loading fails."""
    monkeypatch.setattr(
        infra,
        "get_settings",
        lambda: (_ for _ in ()).throw(RuntimeError("settings error")),
    )

    with pytest.raises(RuntimeError, match="settings error"):
        async with infra.lifespan(mock_app):
            pass


@pytest.mark.asyncio
async def test_lifespan_raises_when_mongodb_fails(monkeypatch, mock_app):
    """Test that lifespan raises when MongoDB connection fails."""
    settings = SimpleNamespace(
        env="test",
        mongodb_uri="mongodb://invalid:27017",
        database_name="testdb",
        redis_url="redis://localhost:6379/0",
        jwt_secret_key="test-secret",
        jwt_algorithm="HS256",
        jwt_issuer="test",
        jwt_audience="test",
        jwt_access_token_expire_days=7,
    )

    class FailingMongoAdmin:
        async def command(self, cmd):
            raise RuntimeError("MongoDB connection failed")

    class FailingMongoClient:
        def __init__(self, *args, **kwargs):
            self.admin = FailingMongoAdmin()

    monkeypatch.setattr(infra, "get_settings", lambda: settings)
    monkeypatch.setattr(infra, "setup_logging", lambda s: None)
    monkeypatch.setattr(infra, "AsyncIOMotorClient", FailingMongoClient)

    with pytest.raises(RuntimeError, match="MongoDB connection failed"):
        async with infra.lifespan(mock_app):
            pass


@pytest.mark.asyncio
async def test_lifespan_raises_when_redis_fails(monkeypatch, mock_app):
    """Test that lifespan raises when Redis connection fails."""
    settings = SimpleNamespace(
        env="test",
        mongodb_uri="mongodb://localhost:27017",
        database_name="testdb",
        review_collection="reviews",
        user_collection="users",
        user_media_entry_collection="user_media_entries",
        redis_url="redis://invalid:6379/0",
        jwt_secret_key="test-secret",
        jwt_algorithm="HS256",
        jwt_issuer="test",
        jwt_audience="test",
        jwt_access_token_expire_days=7,
    )

    class FailingRedis:
        @classmethod
        def from_url(cls, *args, **kwargs):
            raise RuntimeError("Redis connection failed")

    monkeypatch.setattr(infra, "get_settings", lambda: settings)
    monkeypatch.setattr(infra, "setup_logging", lambda s: None)
    monkeypatch.setattr(infra, "AsyncIOMotorClient", FakeMongoClient)
    monkeypatch.setattr(infra, "Redis", FailingRedis)

    with pytest.raises(RuntimeError, match="Redis connection failed"):
        async with infra.lifespan(mock_app):
            pass
