from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from app.repositories.user_repository import UserRepository
from app.models.db.user_models import UserInsert, UserRole, UserUpdate, UserDB


@pytest.fixture
def mock_collection():
    collection = MagicMock()
    collection.insert_one = AsyncMock()
    collection.find_one_and_update = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.name = "users"
    return collection


@pytest.fixture
def repository(mock_collection):
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    return UserRepository(mock_db, "users")


@pytest.fixture
def user_insert():
    return UserInsert(username="testuser", hash_password="hashed", role=UserRole.USER)


@pytest.fixture
def user_update():
    return UserUpdate(username="updateduser")  # type: ignore


@pytest.fixture
def user_db():
    return {
        "_id": ObjectId(),
        "username": "testuser",
        "hash_password": "hashed",
        "role": UserRole.USER,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.mark.asyncio
async def test_insert_user_success(repository, mock_collection, user_insert, user_db):
    inserted_id = ObjectId()
    mock_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.insert_user(user_insert)
    assert result.id == str(inserted_id)
    assert result.username == user_insert.username


@pytest.mark.asyncio
async def test_insert_user_duplicate_key(repository, mock_collection, user_insert):
    mock_collection.insert_one.side_effect = DuplicateKeyError("duplicate")

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        with pytest.raises(DuplicateKeyError):
            await repository.insert_user(user_insert)


@pytest.mark.asyncio
async def test_update_success(repository, mock_collection, user_update, user_db):
    user_id = str(ObjectId())
    mock_collection.find_one_and_update.return_value = user_db

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.update(user_id, user_update)
    assert result.username == user_db["username"]


@pytest.mark.asyncio
async def test_update_not_found(repository, mock_collection, user_update):
    user_id = str(ObjectId())
    mock_collection.find_one_and_update.return_value = None

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.update(user_id, user_update)
    assert result is None


@pytest.mark.asyncio
async def test_delete_success(repository, mock_collection):
    user_id = str(ObjectId())
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.delete(user_id)
    assert result is True


@pytest.mark.asyncio
async def test_delete_not_found(repository, mock_collection):
    user_id = str(ObjectId())
    mock_collection.delete_one.return_value = MagicMock(deleted_count=0)

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.delete(user_id)
    assert result is False


@pytest.mark.asyncio
async def test_get_by_id_found(repository, mock_collection, user_db):
    user_id = str(user_db["_id"])
    mock_collection.find_one.return_value = user_db

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.get_by_id(user_id)
    assert result.username == user_db["username"]


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository, mock_collection):
    user_id = str(ObjectId())
    mock_collection.find_one.return_value = None

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.get_by_id(user_id)
    assert result is None


@pytest.mark.asyncio
async def test_get_by_username_found(repository, mock_collection, user_db):
    mock_collection.find_one.return_value = user_db

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.get_by_username("testuser")
    assert result.username == user_db["username"]


@pytest.mark.asyncio
async def test_get_by_username_not_found(repository, mock_collection):
    mock_collection.find_one.return_value = None

    async def run_db_op_side_effect(logger, op, **kwargs):
        return await op()

    with patch(
        "app.repositories.user_repository.run_db_op",
        new=AsyncMock(side_effect=run_db_op_side_effect),
    ):
        result = await repository.get_by_username("testuser")
    assert result is None
