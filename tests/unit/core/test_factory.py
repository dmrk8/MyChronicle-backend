from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from httpx import AsyncClient, ASGITransport

# --- Fakes for dependencies ---


class FakeMongoAdmin:
    async def command(self, command_name):
        if command_name == "ping":
            return {"ok": 1.0}
        raise RuntimeError("Unknown command")


class FakeMongoClient:
    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        self.admin = FakeMongoAdmin()
        self.closed = False

    def __getitem__(self, name):
        return MagicMock(name=f"db:{name}")

    def close(self):
        self.closed = True


class FakeRedis:
    def __init__(self):
        self.url = None
        self.kwargs = None
        self.closed = False

    @classmethod
    def from_url(cls, url, **kwargs):
        instance = cls()
        instance.url = url
        instance.kwargs = kwargs
        return instance

    async def ping(self):
        return True

    async def close(self):
        self.closed = True


class FakeHTTPClient:
    def __init__(self, timeout):
        self.timeout = timeout
        self.closed = False

    async def aclose(self):
        self.closed = True


# --- Fixtures ---


@pytest.fixture
def fake_settings():
    return SimpleNamespace(
        service_name="test-service",
        env="test",
        mongodb_uri="mongodb://localhost:27017",
        database_name="testdb",
        allow_origins=["*"],
        redis_url="redis://localhost:6379/0",
        jwt_secret_key="test-secret",
        jwt_algorithm="HS256",
        jwt_issuer="test",
        jwt_audience="test",
        jwt_access_token_expire_days=30,
    )


@pytest.fixture(autouse=True)
def patch_factory(monkeypatch):
    monkeypatch.setattr("app.core.factory.setup_logging", lambda settings: None)
    monkeypatch.setattr("app.core.factory.AsyncIOMotorClient", FakeMongoClient)
    monkeypatch.setattr("app.core.factory.Redis", FakeRedis)
    monkeypatch.setattr("app.core.factory.AsyncClient", FakeHTTPClient)
    monkeypatch.setattr("app.core.factory.init_repositories", lambda db, settings: {})


# --- Tests ---


def test_create_app_registers_request_context_middleware(fake_settings):
    from app.core.factory import create_app
    from app.middleware.request_context import RequestContextMiddleware

    app = create_app(fake_settings)
    assert any(
        getattr(middleware, "cls", None) is RequestContextMiddleware
        for middleware in app.user_middleware
    )


@pytest.mark.asyncio
async def test_health_endpoint_returns_expected_response(fake_settings):
    from app.core.factory import create_app

    app = create_app(fake_settings)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == fake_settings.service_name
    assert data["environment"] == fake_settings.env
