import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone

from app.services.media_external_details_service import MediaExternalDetailsService
from app.enums.media_enums import MediaExternalSource, SyncFrequency
from app.models.db.media_external_details_models import (
    MediaExternalDetailsDB,
    MediaExternalDetailsUpdate,
)

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_by_external_id_and_source = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.upsert = AsyncMock()
    return repo

@pytest.fixture
def service(mock_repo):
    return MediaExternalDetailsService(mock_repo)

def test_compute_expiry_high(service):
    expires_at = service._compute_expiry(SyncFrequency.HIGH)
    assert isinstance(expires_at, datetime)
    assert expires_at > datetime.now(timezone.utc)

def test_compute_expiry_medium(service):
    expires_at = service._compute_expiry(SyncFrequency.MEDIUM)
    assert isinstance(expires_at, datetime)
    assert expires_at > datetime.now(timezone.utc)

def test_compute_expiry_low(service):
    expires_at = service._compute_expiry(SyncFrequency.LOW)
    assert expires_at is None

def test_compute_expiry_manual(service):
    expires_at = service._compute_expiry(SyncFrequency.MANUAL)
    assert expires_at is None

def test_is_stale_true(service):
    entry = MagicMock()
    entry.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert service._is_stale(entry) is True

def test_is_stale_false_no_expiry(service):
    entry = MagicMock()
    entry.expires_at = None
    assert service._is_stale(entry) is False

def test_is_stale_false_not_expired(service):
    entry = MagicMock()
    entry.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
    assert service._is_stale(entry) is False

@pytest.mark.asyncio
async def test_get_by_external_id_and_source_updates_last_accessed(service, mock_repo):
    entry = MagicMock()
    mock_repo.get_by_external_id_and_source.return_value = entry
    mock_repo.update.return_value = entry

    result = await service.get_by_external_id_and_source(1, MediaExternalSource.TMDB)
    assert result == entry
    mock_repo.update.assert_awaited_once()
    mock_repo.get_by_external_id_and_source.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_by_external_id_and_source_none(service, mock_repo):
    mock_repo.get_by_external_id_and_source.return_value = None
    result = await service.get_by_external_id_and_source(1, MediaExternalSource.TMDB)
    assert result is None

@pytest.mark.asyncio
async def test_update(service, mock_repo):
    update = MediaExternalDetailsUpdate(payload={"foo": "bar"})
    mock_repo.update.return_value = "updated"
    result = await service.update(1, MediaExternalSource.TMDB, update)
    assert result == "updated"
    mock_repo.update.assert_awaited_once_with(1, MediaExternalSource.TMDB, update)

@pytest.mark.asyncio
async def test_delete(service, mock_repo):
    mock_repo.delete.return_value = True
    result = await service.delete(1, MediaExternalSource.TMDB)
    assert result is True
    mock_repo.delete.assert_awaited_once_with(1, MediaExternalSource.TMDB)

@pytest.mark.asyncio
async def test_upsert(service, mock_repo):
    mock_repo.upsert.return_value = "upserted"
    result = await service.upsert(
        1, MediaExternalSource.TMDB, SyncFrequency.HIGH, {"foo": "bar"}, "json"
    )
    assert result == "upserted"
    mock_repo.upsert.assert_awaited_once()