import pytest
from datetime import datetime, timezone, timedelta

from app.models.db.media_external_details_models import (
    MediaExternalDetailsInsert,
    MediaExternalDetailsDB,
    MediaExternalDetailsUpdate,
)
from app.enums.media_enums import DataFreshnessStatus, MediaExternalSource, SyncFrequency

def test_insert_defaults():
    now = datetime.now(timezone.utc)
    model = MediaExternalDetailsInsert(
        external_id=1,
        external_source=MediaExternalSource.TMDB,
        payload={"foo": "bar"},
        payload_type="json",
        sync_frequency=SyncFrequency.HIGH,
    ) # type: ignore
    assert model.fetched_at is not None
    assert model.last_accessed_at is not None
    assert model.freshness_status == DataFreshnessStatus.FRESH
    assert model.sync_frequency == SyncFrequency.HIGH
    assert model.external_id == 1
    assert model.external_source == MediaExternalSource.TMDB

def test_insert_custom_fields():
    custom_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
    model = MediaExternalDetailsInsert(
        external_id=2,
        external_source=MediaExternalSource.OMDB,
        payload={"bar": "baz"},
        payload_type="xml",
        sync_frequency=SyncFrequency.LOW,
        fetched_at=custom_time,
        last_accessed_at=custom_time,
        freshness_status=DataFreshnessStatus.STALE,
        expires_at=custom_time + timedelta(days=1),
    )
    assert model.fetched_at == custom_time
    assert model.last_accessed_at == custom_time
    assert model.freshness_status == DataFreshnessStatus.STALE
    assert model.expires_at == custom_time + timedelta(days=1)

def test_update_to_update_dict():
    update = MediaExternalDetailsUpdate(
        payload={"foo": "bar"},
        payload_type="json",
        freshness_status=DataFreshnessStatus.FRESH,
    )
    update_dict = update.to_update_dict()
    assert update_dict["payload"] == {"foo": "bar"}
    assert update_dict["payload_type"] == "json"
    assert update_dict["freshness_status"] == DataFreshnessStatus.FRESH

def test_update_to_update_dict_empty():
    update = MediaExternalDetailsUpdate()
    with pytest.raises(ValueError):
        update.to_update_dict()