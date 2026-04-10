import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from bson import ObjectId
from pymongo import ReturnDocument

import app.repositories.user_repository as repo_module
from app.models.user_models import UserInsert, UserRole, UserUpdate
from app.repositories.user_repository import UserRepository


@pytest.fixture
def mock_collection():
    collection = MagicMock()
    collection.insert_one = AsyncMock()
    collection.find_one_and_update = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.find_one = AsyncMock()
    return collection


@pytest.fixture
def repository(mock_collection):
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    return UserRepository(mock_db, "users")


@pytest.fixture
def sample_user_insert():
    return UserInsert(
        username="anil",
        hash_password="hashed-password",
        role=UserRole.USER,
    )


@pytest.fixture
def passthrough_run_db_op(monkeypatch):
    async def _run_db_op(_logger, op, **_kwargs):
        return await op()

    monkeypatch.setattr(repo_module, "run_db_op", _run_db_op)


@pytest.mark.asyncio
async def test_create_inserts_payload_and_returns_model(
    repository, mock_collection, sample_user_insert, passthrough_run_db_op
):
    inserted_id = ObjectId()
    mock_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

    result = await repository.create(sample_user_insert)

    assert result.id == str(inserted_id)
    assert result.username == sample_user_insert.username
    assert result.role == UserRole.USER
    assert result.hash_password == sample_user_insert.hash_password
    mock_collection.insert_one.assert_awaited_once_with(sample_user_insert.model_dump())


@pytest.mark.asyncio
async def test_update_scopes_by_object_id_and_returns_updated_model(
    repository, mock_collection, passthrough_run_db_op
):
    user_id = ObjectId()
    now = datetime.now(timezone.utc)
    update_data = UserUpdate(username="anil-new") # type: ignore
    updated_doc = {
        "_id": user_id,
        "username": "anil-new",
        "role": UserRole.USER,
        "hash_password": "hashed-password",
        "created_at": now,
        "updated_at": now,
    }
    mock_collection.find_one_and_update.return_value = updated_doc

    result = await repository.update(str(user_id), update_data)

    assert result is not None
    assert result.id == str(user_id)
    assert result.username == "anil-new"

    call = mock_collection.find_one_and_update.await_args
    assert call.args[0] == {"_id": user_id}
    assert "$set" in call.args[1]
    assert call.args[1]["$set"]["username"] == "anil-new"
    assert "updated_at" in call.args[1]["$set"]
    assert call.kwargs["return_document"] == ReturnDocument.AFTER


@pytest.mark.asyncio
async def test_update_returns_none_when_not_found(
    repository, mock_collection, passthrough_run_db_op
):
    user_id = ObjectId()
    mock_collection.find_one_and_update.return_value = None

    result = await repository.update(str(user_id), UserUpdate(username="missing")) # type: ignore

    assert result is None


@pytest.mark.asyncio
async def test_delete_scopes_by_object_id(repository, mock_collection, passthrough_run_db_op):
    user_id = ObjectId()
    delete_result = MagicMock(deleted_count=1)
    mock_collection.delete_one.return_value = delete_result

    result = await repository.delete(str(user_id))

    assert result.deleted_count == 1
    mock_collection.delete_one.assert_awaited_once_with({"_id": user_id})


@pytest.mark.asyncio
async def test_get_by_id_returns_user_when_found(
    repository, mock_collection, passthrough_run_db_op
):
    user_id = ObjectId()
    now = datetime.now(timezone.utc)
    doc = {
        "_id": user_id,
        "username": "anil",
        "role": UserRole.USER,
        "hash_password": "hashed-password",
        "created_at": now,
        "updated_at": now,
    }
    mock_collection.find_one.return_value = doc

    result = await repository.get_by_id(str(user_id))

    assert result is not None
    assert result.id == str(user_id)
    assert result.username == "anil"
    mock_collection.find_one.assert_awaited_once_with({"_id": user_id})


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_missing(
    repository, mock_collection, passthrough_run_db_op
):
    user_id = ObjectId()
    mock_collection.find_one.return_value = None

    result = await repository.get_by_id(str(user_id))

    assert result is None


@pytest.mark.asyncio
async def test_is_username_exists_returns_true_when_doc_present(
    repository, mock_collection, passthrough_run_db_op
):
    mock_collection.find_one.return_value = {"_id": ObjectId(), "username": "anil"}

    exists = await repository.is_username_exists("anil")

    assert exists is True
    mock_collection.find_one.assert_awaited_once_with({"username": "anil"})


@pytest.mark.asyncio
async def test_is_username_exists_returns_false_when_missing(
    repository, mock_collection, passthrough_run_db_op
):
    mock_collection.find_one.return_value = None

    exists = await repository.is_username_exists("anil")

    assert exists is False


@pytest.mark.asyncio
async def test_get_by_username_returns_user_when_found(
    repository, mock_collection, passthrough_run_db_op
):
    user_id = ObjectId()
    now = datetime.now(timezone.utc)
    doc = {
        "_id": user_id,
        "username": "anil",
        "role": UserRole.USER,
        "hash_password": "hashed-password",
        "created_at": now,
        "updated_at": now,
    }
    mock_collection.find_one.return_value = doc

    result = await repository.get_by_username("anil")

    assert result is not None
    assert result.id == str(user_id)
    assert result.username == "anil"
    mock_collection.find_one.assert_awaited_once_with({"username": "anil"})


@pytest.mark.asyncio
async def test_get_by_username_returns_none_when_missing(
    repository, mock_collection, passthrough_run_db_op
):
    mock_collection.find_one.return_value = None

    result = await repository.get_by_username("anil")

    assert result is None
