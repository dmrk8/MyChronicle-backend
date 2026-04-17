import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from datetime import datetime, timezone
from app.repositories.media_external_details_repository import (
    MediaExternalDetailsRepository,
)
from app.models.db.media_external_details_models import (
    MediaExternalDetailsInsert,
    MediaExternalDetailsUpdate,
    MediaExternalDetailsDB,
)
from app.enums.media_enums import (
    MediaExternalSource,
    SyncFrequency,
    DataFreshnessStatus,
)


@pytest.fixture
def fake_db():
    db = MagicMock()
    db.__getitem__.return_value = AsyncMock()
    return db


@pytest.fixture
def repo(fake_db):
    return MediaExternalDetailsRepository(fake_db, "test_collection")


@pytest.fixture

def insert_data():
    return MediaExternalDetailsInsert(
        external_id=123,
        external_source=MediaExternalSource.TMDB,
        fetched_at=datetime(2026, 4, 17, 0, 0, 0, tzinfo=timezone.utc),
        last_accessed_at=datetime(2026, 4, 17, 0, 0, 0, tzinfo=timezone.utc),
        expires_at=None,
        payload={"foo": "bar"},
        payload_type="json",
        freshness_status=DataFreshnessStatus.FRESH,
        sync_frequency=SyncFrequency.HIGH,
    )


@pytest.mark.asyncio
async def test_create(repo, insert_data):
    repo.collection.find_one_and_update = AsyncMock(return_value={"_id": "abc123", **insert_data.model_dump()})
    result = await repo.upsert(insert_data)
    assert result.id == "abc123"
    assert result.external_id == insert_data.external_id

@pytest.mark.asyncio
async def test_upsert(repo, insert_data):
    repo.collection.find_one_and_update = AsyncMock(
        return_value={"_id": "abc123", **insert_data.model_dump()}
    )
    result = await repo.upsert(insert_data)
    assert result.id == "abc123"
    assert result.external_id == insert_data.external_id


@pytest.mark.asyncio
async def test_get_by_external_id_and_source(repo, insert_data):
    repo.collection.find_one = AsyncMock(
        return_value={"_id": "abc123", **insert_data.model_dump()}
    )
    result = await repo.get_by_external_id_and_source(
        insert_data.external_id, insert_data.external_source
    )
    assert result.id == "abc123"
    assert result.external_id == insert_data.external_id


@pytest.mark.asyncio
async def test_update(repo, insert_data):
    update = MediaExternalDetailsUpdate(payload={"bar": "baz"})
    repo.collection.find_one_and_update = AsyncMock(
        return_value={
            "_id": "abc123",
            **insert_data.model_dump(),
            "payload": {"bar": "baz"},
        }
    )
    result = await repo.update(
        insert_data.external_id, insert_data.external_source, update
    )
    assert result.id == "abc123"
    assert result.payload == {"bar": "baz"}


@pytest.mark.asyncio
async def test_delete(repo, insert_data):
    repo.collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    result = await repo.delete(insert_data.external_id, insert_data.external_source)
    assert result is True
