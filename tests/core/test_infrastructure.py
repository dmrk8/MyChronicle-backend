from types import SimpleNamespace

import pytest

from app.core import infrastructure as infra


class FakeMongoClient:
    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        self.closed = False

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


class FakeRedisClient:
    def __init__(self):
        self.closed = False

    async def close(self):
        self.closed = True


@pytest.fixture(autouse=True)
def reset_state():
    FakeAsyncClient.instances = []

    infra.state.settings = None
    infra.state.mongo_client = None
    infra.state.anilist_client = None
    infra.state.tmdb_client = None

    yield

    infra.state.settings = None
    infra.state.mongo_client = None
    infra.state.anilist_client = None
    infra.state.tmdb_client = None


@pytest.mark.asyncio
async def test_lifespan_initializes_and_closes_clients(monkeypatch):
    settings = SimpleNamespace(env="test", mongodb_uri="mongodb://localhost:27017")
    setup_calls = []

    monkeypatch.setattr(infra, "get_settings", lambda: settings)
    monkeypatch.setattr(infra, "setup_logging", lambda s: setup_calls.append(s))
    monkeypatch.setattr(infra, "AsyncIOMotorClient", FakeMongoClient)
    monkeypatch.setattr(infra, "AsyncClient", FakeAsyncClient)

    async with infra.lifespan(app=None):
        assert infra.state.settings is settings
        assert isinstance(infra.state.mongo_client, FakeMongoClient)
        assert infra.state.mongo_client.uri == settings.mongodb_uri
        assert infra.state.mongo_client.kwargs == {"maxPoolSize": 10, "minPoolSize": 2}

        assert len(FakeAsyncClient.instances) == 2
        assert all(client.timeout == 10.0 for client in FakeAsyncClient.instances)
        assert setup_calls == [settings]

    assert infra.state.mongo_client.closed is True
    assert all(client.closed is True for client in FakeAsyncClient.instances)



@pytest.mark.asyncio
async def test_lifespan_raises_when_settings_fail(monkeypatch):
    monkeypatch.setattr(infra, "get_settings", lambda: (_ for _ in ()).throw(RuntimeError("settings error")))

    with pytest.raises(RuntimeError, match="settings error"):
        async with infra.lifespan(app=None):
            pass


@pytest.mark.asyncio
async def test_lifespan_raises_when_mongodb_connection_fails(monkeypatch):
    settings = SimpleNamespace(env="test", mongodb_uri="mongodb://localhost:27017")

    def raise_mongo(*args, **kwargs):
        raise RuntimeError("mongo error")

    monkeypatch.setattr(infra, "get_settings", lambda: settings)
    monkeypatch.setattr(infra, "setup_logging", lambda _: None)
    monkeypatch.setattr(infra, "AsyncIOMotorClient", raise_mongo)

    with pytest.raises(RuntimeError, match="mongo error"):
        async with infra.lifespan(app=None):
            pass
