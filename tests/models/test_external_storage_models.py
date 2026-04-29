from bson import ObjectId
import pytest
from datetime import datetime, timedelta, timezone

from app.models.api.tmdb_models import TMDBCollection, TMDBMovieDetail
from app.models.db.external_storage_models import (
    ExternalDataUpsert,
    ExternalDataDB,
    ExternalDataUpdate,
    MovieWithCollection,
)
from app.enums.media_enums import (
    DataFreshnessStatus,
    MediaExternalSource,
    MediaType,
    StoredDataType,
)


# ---- Minimal fake payload ----
def FakePayload():

    movie = TMDBMovieDetail(
        adult=False,
        id=1,
    )  # type: ignore
    collection = TMDBCollection(
        id=1,
        name="Fake Collection",
    )  # type: ignore
    return MovieWithCollection(movie=movie, collection=collection)


def test_external_data_upsert_sets_defaults():
    obj = ExternalDataUpsert(
        external_id=123,
        external_source=MediaExternalSource.TMDB,
        media_type=MediaType.MOVIE,
        payload=FakePayload(),
        payload_type=StoredDataType.MEDIA_DETAILS,
    )

    assert obj.fetched_at is not None
    assert obj.last_accessed_at is not None
    assert obj.expires_at is not None

    assert obj.freshness_status == DataFreshnessStatus.FRESH

    delta = obj.expires_at - obj.fetched_at
    assert timedelta(days=6) < delta < timedelta(days=8)


def test_external_data_upsert_preserves_provided_timestamps():
    now = datetime.now(timezone.utc)

    obj = ExternalDataUpsert(
        external_id=1,
        external_source=MediaExternalSource.TMDB,
        media_type=MediaType.MOVIE,
        payload=FakePayload(),
        payload_type=StoredDataType.MEDIA_DETAILS,
        fetched_at=now,
        last_accessed_at=now,
        freshness_status=DataFreshnessStatus.STALE,
    )

    assert obj.fetched_at == now
    assert obj.last_accessed_at == now
    assert obj.freshness_status == DataFreshnessStatus.STALE


def test_external_data_db_coerces_object_id():
    obj = ExternalDataDB(
        _id=123456,  # int should become str # type: ignore
        external_id=1,
        external_source=MediaExternalSource.TMDB,
        media_type=MediaType.MOVIE,
        payload=FakePayload(),
        payload_type=StoredDataType.MEDIA_DETAILS,
        fetched_at=datetime.now(timezone.utc),
        last_accessed_at=datetime.now(timezone.utc),
        freshness_status=DataFreshnessStatus.FRESH,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    assert isinstance(obj.id, str)
    assert obj.id == "123456"


def test_external_data_update_to_update_dict_success():
    update = ExternalDataUpdate(
        expires_at=datetime.now(timezone.utc),
    )

    result = update.model_dump(exclude_unset=True)

    assert "expires_at" in result



def test_external_data_update_partial_fields():
    update = ExternalDataUpdate(last_accessed_at=datetime.now(timezone.utc))

    result = update.model_dump(exclude_unset=True)

    assert result == {"last_accessed_at": update.last_accessed_at}

def test_external_data_update_empty():
    with pytest.raises(ValueError):
        ExternalDataUpdate().model_dump(exclude_unset=True)
        
def test_external_data_update_valid():
    update = ExternalDataUpdate(
        expires_at=datetime.now(timezone.utc),
        freshness_status=DataFreshnessStatus.STALE,
    )

    result = update.model_dump(exclude_unset=True)

    assert "expires_at" in result
    assert "freshness_status" in result