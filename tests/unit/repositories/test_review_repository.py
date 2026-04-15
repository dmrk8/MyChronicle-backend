import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from bson import ObjectId

import app.repositories.review_repository as repo_module
from app.models.review_models import ReviewInsert, ReviewUpdate
from app.repositories.review_repository import ReviewRepository


@pytest.fixture
def mock_collection():
    collection = MagicMock()
    collection.count_documents = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.find_one_and_update = AsyncMock()
    collection.find = MagicMock()
    collection.find_one = AsyncMock()
    collection.delete_many = AsyncMock()
    return collection


@pytest.fixture
def repository(mock_collection):
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    return ReviewRepository(mock_db, "reviews")


@pytest.fixture
def sample_insert():
    return ReviewInsert(
        user_media_entry_id="entry-1",
        user_id="user-1",
        rating=8.5,
        review="Great",
    )  # type: ignore


@pytest.fixture
def passthrough_run_db_op(monkeypatch):
    async def _run_db_op(_logger, op, **_kwargs):
        return await op()

    monkeypatch.setattr(repo_module, "run_db_op", _run_db_op)


@pytest.mark.asyncio
async def test_is_exists_scopes_by_review_user_and_entry_id(
    repository, mock_collection, passthrough_run_db_op
):
    review_id = ObjectId()
    mock_collection.count_documents.return_value = 1

    exists = await repository.is_exists(str(review_id), "user-1", "entry-1")

    assert exists is True
    mock_collection.count_documents.assert_awaited_once_with(
        {"_id": review_id, "user_id": "user-1", "user_media_entry_id": "entry-1"},
        limit=1,
    )


@pytest.mark.asyncio
async def test_is_exists_returns_false_when_missing(
    repository, mock_collection, passthrough_run_db_op
):
    review_id = ObjectId()
    mock_collection.count_documents.return_value = 0

    exists = await repository.is_exists(str(review_id), "user-1", "entry-1")

    assert exists is False


@pytest.mark.asyncio
async def test_create_review_inserts_dumped_payload(
    repository, mock_collection, sample_insert, passthrough_run_db_op
):
    insert_result = MagicMock(inserted_id=ObjectId())
    mock_collection.insert_one.return_value = insert_result

    result = await repository.create_review(sample_insert)

    assert result.id == str(insert_result.inserted_id)
    assert result.user_media_entry_id == "entry-1"
    assert result.user_id == "user-1"
    assert result.rating == 8.5
    assert result.review == "Great"
    mock_collection.insert_one.assert_awaited_once_with(sample_insert.model_dump())


@pytest.mark.asyncio
async def test_delete_review_scopes_by_review_user_and_entry_id(
    repository, mock_collection, passthrough_run_db_op
):
    review_id = ObjectId()
    delete_result = MagicMock(deleted_count=1)
    mock_collection.delete_one.return_value = delete_result

    result = await repository.delete_review(str(review_id), "user-1", "entry-1")

    assert result.deleted_count == 1
    mock_collection.delete_one.assert_awaited_once_with(
        {"_id": review_id, "user_id": "user-1", "user_media_entry_id": "entry-1"}
    )


@pytest.mark.asyncio
async def test_update_review_scopes_by_review_user_and_entry_id(
    repository, mock_collection, passthrough_run_db_op
):
    review_id = ObjectId()
    now = datetime.now(timezone.utc)
    update = ReviewUpdate(rating=9.0, reviewProgress=20)  # type: ignore

    updated_doc = {
        "_id": review_id,
        "user_media_entry_id": "entry-1",
        "user_id": "user-1",
        "rating": 9.0,
        "review": "Great",
        "review_progress": 20,
        "created_at": now,
        "updated_at": now,
    }
    mock_collection.find_one_and_update.return_value = updated_doc

    result = await repository.update_review(str(review_id), "entry-1", update, "user-1")

    assert result is not None
    assert result.id == str(review_id)
    assert result.user_id == "user-1"
    assert result.rating == 9.0
    assert result.review_progress == 20

    call = mock_collection.find_one_and_update.await_args
    assert call.args[0] == {
        "_id": review_id,
        "user_id": "user-1",
        "user_media_entry_id": "entry-1",
    }
    assert "$set" in call.args[1]
    assert call.args[1]["$set"]["rating"] == 9.0
    assert call.args[1]["$set"]["review_progress"] == 20
    assert "updated_at" in call.args[1]["$set"]


@pytest.mark.asyncio
async def test_get_review_by_id_scopes_by_user_and_entry_and_maps_model(
    repository, mock_collection, passthrough_run_db_op
):
    review_id = ObjectId()
    now = datetime.now(timezone.utc)
    doc = {
        "_id": review_id,
        "user_media_entry_id": "entry-1",
        "user_id": "user-1",
        "rating": 8,
        "review": "Nice",
        "created_at": now,
        "updated_at": now,
    }
    mock_collection.find_one.return_value = doc

    result = await repository.get_review_by_id(str(review_id), "user-1", "entry-1")

    assert result is not None
    assert result.id == str(review_id)
    assert result.user_id == "user-1"
    mock_collection.find_one.assert_awaited_once_with(
        {"_id": review_id, "user_id": "user-1", "user_media_entry_id": "entry-1"}
    )


@pytest.mark.asyncio
async def test_get_review_by_id_returns_none_when_missing(
    repository, mock_collection, passthrough_run_db_op
):
    review_id = ObjectId()
    mock_collection.find_one.return_value = None

    result = await repository.get_review_by_id(str(review_id), "user-1", "entry-1")

    assert result is None


@pytest.mark.asyncio
async def test_get_reviews_by_entry_and_user_scopes_query(
    repository, mock_collection, passthrough_run_db_op
):
    now = datetime.now(timezone.utc)
    doc = {
        "_id": ObjectId(),
        "user_media_entry_id": "entry-1",
        "user_id": "user-1",
        "rating": 7,
        "review": "Solid",
        "created_at": now,
        "updated_at": now,
    }

    cursor = MagicMock()
    cursor.__aiter__.return_value = [doc]
    mock_collection.find.return_value = cursor

    results = await repository.get_reviews_by_user_media_entry_id_and_user_id(
        "entry-1", "user-1"
    )

    assert len(results) == 1
    assert results[0].user_id == "user-1"
    mock_collection.find.assert_called_once_with(
        {"user_media_entry_id": "entry-1", "user_id": "user-1"}
    )


@pytest.mark.asyncio
async def test_count_reviews_by_entry_and_user_scopes_query(
    repository, mock_collection, passthrough_run_db_op
):
    mock_collection.count_documents.return_value = 4

    count = await repository.count_reviews_by_user_media_entry_id("entry-1", "user-1")

    assert count == 4
    mock_collection.count_documents.assert_awaited_once_with(
        {"user_media_entry_id": "entry-1", "user_id": "user-1"}
    )


@pytest.mark.asyncio
async def test_delete_reviews_by_entry_and_user_scopes_query(
    repository, mock_collection, passthrough_run_db_op
):
    delete_result = MagicMock(deleted_count=3)
    mock_collection.delete_many.return_value = delete_result

    result = await repository.delete_reviews_by_user_media_entry_id("entry-1", "user-1")

    assert result.deleted_count == 3
    mock_collection.delete_many.assert_awaited_once_with(
        {"user_media_entry_id": "entry-1", "user_id": "user-1"}
    )


@pytest.mark.asyncio
async def test_delete_by_user_id_scopes_query(
    repository, mock_collection, passthrough_run_db_op
):
    delete_result = MagicMock(deleted_count=5)
    mock_collection.delete_many.return_value = delete_result

    result = await repository.delete_by_user_id("user-1")

    assert result.deleted_count == 5
    mock_collection.delete_many.assert_awaited_once_with({"user_id": "user-1"})
