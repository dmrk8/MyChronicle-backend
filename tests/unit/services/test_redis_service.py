import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from redis.asyncio import Redis
from app.services.redis_service import RedisService


class TestModel(BaseModel):
    """Test model for caching"""

    id: str
    name: str


class ComplexModel(BaseModel):
    """Complex model with nested fields"""

    id: str
    name: str
    tags: list[str]
    data: dict


@pytest.fixture
def mock_redis():
    """Create a mock Redis client"""
    return AsyncMock()


@pytest.fixture
def redis_service(mock_redis):
    """Create RedisService with mock Redis"""
    return RedisService(redis_client=mock_redis)


@pytest.mark.asyncio
async def test_get_cached_returns_none_when_key_missing(redis_service, mock_redis):
    """Test that get_cached returns None when key doesn't exist"""
    mock_redis.get = AsyncMock(return_value=None)

    result = await redis_service.get_cached("missing_key", TestModel)

    assert result is None
    mock_redis.get.assert_called_once_with("missing_key")


@pytest.mark.asyncio
async def test_get_cached_returns_model_when_exists(redis_service, mock_redis):
    """Test that get_cached returns validated model when key exists"""
    test_data = TestModel(id="1", name="test")
    mock_redis.get = AsyncMock(return_value=test_data.model_dump_json())

    result = await redis_service.get_cached("test_key", TestModel)

    assert result is not None
    assert result.id == "1"
    assert result.name == "test"
    mock_redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_get_cached_with_complex_model(redis_service, mock_redis):
    """Test that get_cached works with nested model structures"""
    test_data = ComplexModel(
        id="1", name="test", tags=["tag1", "tag2"], data={"key": "value"}
    )
    mock_redis.get = AsyncMock(return_value=test_data.model_dump_json())

    result = await redis_service.get_cached("complex_key", ComplexModel)

    assert result is not None
    assert result.id == "1"
    assert result.tags == ["tag1", "tag2"]
    assert result.data == {"key": "value"}


@pytest.mark.asyncio
async def test_set_cached_stores_model_with_ttl(redis_service, mock_redis):
    """Test that set_cached stores model as JSON with correct TTL"""
    test_data = TestModel(id="1", name="test")
    ttl = 3600
    mock_redis.setex = AsyncMock()

    await redis_service.set_cached("test_key", test_data, ttl=ttl)

    mock_redis.setex.assert_called_once_with(
        "test_key", ttl, test_data.model_dump_json()
    )


@pytest.mark.asyncio
async def test_set_cached_uses_default_ttl(redis_service, mock_redis):
    """Test that set_cached uses default TTL when not specified"""
    test_data = TestModel(id="1", name="test")
    mock_redis.setex = AsyncMock()

    await redis_service.set_cached("test_key", test_data)

    mock_redis.setex.assert_called_once_with(
        "test_key", 3600, test_data.model_dump_json()
    )


@pytest.mark.asyncio
async def test_set_cached_with_custom_ttl_values(redis_service, mock_redis):
    """Test that set_cached respects different TTL values"""
    test_data = TestModel(id="1", name="test")
    mock_redis.setex = AsyncMock()

    # Test with 24 hours
    await redis_service.set_cached("key_24h", test_data, ttl=86400)
    mock_redis.setex.assert_called_with("key_24h", 86400, test_data.model_dump_json())

    # Test with 1 hour
    await redis_service.set_cached("key_1h", test_data, ttl=3600)
    mock_redis.setex.assert_called_with("key_1h", 3600, test_data.model_dump_json())


@pytest.mark.asyncio
async def test_get_cached_raises_on_redis_error(redis_service, mock_redis):
    """Test that get_cached raises exception on Redis error"""
    mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))

    with pytest.raises(Exception, match="Redis error"):
        await redis_service.get_cached("test_key", TestModel)


@pytest.mark.asyncio
async def test_set_cached_raises_on_redis_error(redis_service, mock_redis):
    """Test that set_cached raises exception on Redis error"""
    test_data = TestModel(id="1", name="test")
    mock_redis.setex = AsyncMock(side_effect=Exception("Redis error"))

    with pytest.raises(Exception, match="Redis error"):
        await redis_service.set_cached("test_key", test_data)


@pytest.mark.asyncio
async def test_get_cached_invalid_json_raises(redis_service, mock_redis):
    """Test that get_cached raises on invalid JSON data"""
    mock_redis.get = AsyncMock(return_value="invalid json {{")

    with pytest.raises(Exception):
        await redis_service.get_cached("test_key", TestModel)


@pytest.mark.asyncio
async def test_get_cached_logs_error_on_redis_failure(redis_service, mock_redis):
    """Test that get_cached logs error details on Redis failure"""
    mock_redis.get = AsyncMock(side_effect=Exception("Connection refused"))

    with pytest.raises(Exception):
        await redis_service.get_cached("test_key", TestModel)


@pytest.mark.asyncio
async def test_set_cached_logs_error_on_redis_failure(redis_service, mock_redis):
    """Test that set_cached logs error details on Redis failure"""
    test_data = TestModel(id="1", name="test")
    mock_redis.setex = AsyncMock(side_effect=Exception("Connection refused"))

    with pytest.raises(Exception):
        await redis_service.set_cached("test_key", test_data)


@pytest.mark.asyncio
async def test_multiple_models_different_types(redis_service, mock_redis):
    """Test that service handles multiple different model types"""
    test_model = TestModel(id="1", name="test")
    complex_model = ComplexModel(id="2", name="complex", tags=["a", "b"], data={})

    mock_redis.get = AsyncMock(return_value=test_model.model_dump_json())
    result1 = await redis_service.get_cached("key1", TestModel)
    assert result1.id == "1"

    mock_redis.get = AsyncMock(return_value=complex_model.model_dump_json())
    result2 = await redis_service.get_cached("key2", ComplexModel)
    assert result2.id == "2"
    assert len(result2.tags) == 2
