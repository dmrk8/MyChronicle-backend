import pytest
from unittest.mock import AsyncMock, MagicMock

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

import app.repositories.user_media_entry_repository as repo_module
from app.enums.user_media_entry_enums import (
    MediaExternalSource,
    MediaType,
    UserMediaEntryStatus,
)
from app.models.user_media_entry_models import UserMediaEntryInsert, UserMediaEntryUpdate
from app.repositories.user_media_entry_repository import UserMediaEntryRepository


@pytest.fixture
def mock_collection():
    collection = MagicMock()
    collection.create_index = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.find_one_and_update = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.count_documents = AsyncMock()
    return collection


@pytest.fixture
def repository(mock_collection):
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    return UserMediaEntryRepository(mock_db, "user_media_entries")


@pytest.fixture
def sample_entry_insert():
    return UserMediaEntryInsert(
        user_id="user-1",
        externalId=1001,
        externalSource=MediaExternalSource.ANILIST,
        mediaType=MediaType.ANIME,
        title="Steins;Gate",
        status=UserMediaEntryStatus.PLANNING,
    ) # type: ignore


@pytest.fixture
def passthrough_run_db_op(monkeypatch):
    async def _run_db_op(_logger, op, **_kwargs):
        return await op()

    monkeypatch.setattr(repo_module, "run_db_op", _run_db_op)


@pytest.mark.asyncio
async def test_init_indexes_creates_unique_compound_index(repository, mock_collection):
    await repository.init_indexes()

    mock_collection.create_index.assert_awaited_once_with(
        [("user_id", 1), ("external_id", 1), ("external_source", 1)],
        unique=True,
        name="user_external_unique_idx",
    )


@pytest.mark.asyncio
async def test_create_entry_returns_created_model(
    repository, mock_collection, sample_entry_insert, passthrough_run_db_op
):
    inserted_id = ObjectId()
    mock_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

    result = await repository.create_entry(sample_entry_insert)

    assert result.id == str(inserted_id)
    assert result.user_id == sample_entry_insert.user_id
    assert result.external_id == sample_entry_insert.external_id
    mock_collection.insert_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_entry_raises_duplicate_key_error_and_bubbles(
    repository, mock_collection, sample_entry_insert, passthrough_run_db_op
):
    mock_collection.insert_one.side_effect = DuplicateKeyError("duplicate")

    with pytest.raises(DuplicateKeyError):
        await repository.create_entry(sample_entry_insert)


@pytest.mark.asyncio
async def test_get_entry_by_id_returns_entry_when_found(
    repository, mock_collection, passthrough_run_db_op
):
    entry_id = ObjectId()
    doc = {
        "_id": entry_id,
        "user_id": "user-1",
        "external_id": 1001,
        "external_source": MediaExternalSource.ANILIST,
        "media_type": MediaType.ANIME,
        "title": "Steins;Gate",
        "status": UserMediaEntryStatus.CURRENT,
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
    }
    mock_collection.find_one.return_value = doc

    result = await repository.get_entry_by_id(str(entry_id), "user-1")

    assert result is not None
    assert result.id == str(entry_id)
    mock_collection.find_one.assert_awaited_once_with(
        {"_id": entry_id, "user_id": "user-1"}
    )


@pytest.mark.asyncio
async def test_get_entry_by_id_returns_none_when_missing(
    repository, mock_collection, passthrough_run_db_op
):
    entry_id = ObjectId()
    mock_collection.find_one.return_value = None

    result = await repository.get_entry_by_id(str(entry_id), "user-1")

    assert result is None


@pytest.mark.asyncio
async def test_update_entry_applies_owner_scope_and_returns_updated_doc(
    repository, mock_collection, passthrough_run_db_op
):
    entry_id = ObjectId()
    update = UserMediaEntryUpdate(status=UserMediaEntryStatus.COMPLETED) # type: ignore
    updated_doc = {
        "_id": entry_id,
        "user_id": "user-1",
        "external_id": 1001,
        "external_source": MediaExternalSource.ANILIST,
        "media_type": MediaType.ANIME,
        "title": "Steins;Gate",
        "status": UserMediaEntryStatus.COMPLETED,
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-02T00:00:00+00:00",
    }
    mock_collection.find_one_and_update.return_value = updated_doc

    result = await repository.update_entry(str(entry_id), "user-1", update)

    assert result is not None
    assert result.status == UserMediaEntryStatus.COMPLETED

    call = mock_collection.find_one_and_update.await_args
    assert call.args[0] == {"_id": entry_id, "user_id": "user-1"}
    assert "$set" in call.args[1]
    assert call.args[1]["$set"]["status"] == UserMediaEntryStatus.COMPLETED
    assert "updated_at" in call.args[1]["$set"]
    assert call.kwargs["return_document"] == ReturnDocument.AFTER


@pytest.mark.asyncio
async def test_delete_entry_uses_owner_scope(repository, mock_collection, passthrough_run_db_op):
    entry_id = ObjectId()
    delete_result = MagicMock(deleted_count=1)
    mock_collection.delete_one.return_value = delete_result

    result = await repository.delete_entry(str(entry_id), "user-1")

    assert result.deleted_count == 1
    mock_collection.delete_one.assert_awaited_once_with(
        {"_id": entry_id, "user_id": "user-1"}
    )


@pytest.mark.asyncio
async def test_count_entries_by_user_id(repository, mock_collection, passthrough_run_db_op):
    mock_collection.count_documents.return_value = 3

    result = await repository.count_entries_by_user_id("user-1")

    assert result == 3
    mock_collection.count_documents.assert_awaited_once_with({"user_id": "user-1"})


@pytest.mark.asyncio
async def test_count_entries_scopes_filters_with_user_id(
    repository, mock_collection, passthrough_run_db_op
):
    filters = {"status": UserMediaEntryStatus.CURRENT}
    mock_collection.count_documents.return_value = 7

    result = await repository.count_entries("user-1", filters)

    assert result == 7
    assert filters == {"status": UserMediaEntryStatus.CURRENT}
    mock_collection.count_documents.assert_awaited_once_with(
        {"status": UserMediaEntryStatus.CURRENT, "user_id": "user-1"}
    )
@pytest.mark.asyncio
async def test_get_entries_scopes_filters_with_user_id_and_applies_pagination(
    repository, mock_collection, passthrough_run_db_op
):
    filters = {"status": UserMediaEntryStatus.CURRENT}
    entry_id = ObjectId()
    docs = [
        {
            "_id": entry_id,
            "user_id": "user-1",
            "external_id": 1001,
            "external_source": MediaExternalSource.ANILIST,
            "media_type": MediaType.ANIME,
            "title": "Steins;Gate",
            "status": UserMediaEntryStatus.CURRENT,
            "created_at": "2025-01-01T00:00:00+00:00",
            "updated_at": "2025-01-02T00:00:00+00:00",
        }
    ]

    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.__aiter__.return_value = docs
    mock_collection.find.return_value = cursor

    results = await repository.get_entries(
        user_id="user-1",
        filters=filters,
        page=2,
        per_page=5,
        sort_by="updated_at",
        sort_order=-1,
    )

    assert len(results) == 1
    assert results[0].id == str(entry_id)
    assert filters == {"status": UserMediaEntryStatus.CURRENT}

    mock_collection.find.assert_called_once_with(
        {"status": UserMediaEntryStatus.CURRENT, "user_id": "user-1"}
    )
    cursor.sort.assert_called_once_with("updated_at", -1)
    cursor.skip.assert_called_once_with(5)
    cursor.limit.assert_called_once_with(5)

