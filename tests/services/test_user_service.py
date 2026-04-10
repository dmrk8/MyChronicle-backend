import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from pymongo.errors import DuplicateKeyError

from app.auth.password_handler import PasswordHandler
from app.core.exceptions import AuthenticationError, ConflictException
from app.models.user_models import UserDB, UserRole, UserUpdate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


@pytest.fixture
def mock_user_repository():
    return MagicMock(spec=UserRepository)


@pytest.fixture
def mock_password_handler():
    return MagicMock(spec=PasswordHandler)


@pytest.fixture
def user_service(mock_user_repository, mock_password_handler):
    return UserService(
        user_repository=mock_user_repository,
        password_handler=mock_password_handler,
    )


def create_user_db(**overrides):
    defaults = {
        "_id": "507f1f77bcf86cd799439011",
        "username": "testuser",
        "hash_password": "hashed_pwd",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "role": UserRole.USER,
    }
    defaults.update(overrides)
    return UserDB(**defaults)


@pytest.mark.asyncio
async def test_create_user_success(
    user_service, mock_user_repository, mock_password_handler
):
    created_user = create_user_db(username="newuser")
    mock_password_handler.hash_password.return_value = "hashed_pwd"
    mock_user_repository.create = AsyncMock(return_value=created_user)

    result = await user_service.create_user("newuser", "plain_pwd")

    assert result.id == "507f1f77bcf86cd799439011"
    assert result.username == "newuser"
    assert result.role == UserRole.USER
    mock_password_handler.hash_password.assert_called_once_with("plain_pwd")

    inserted_user = mock_user_repository.create.call_args.args[0]
    assert inserted_user.username == "newuser"
    assert inserted_user.hash_password == "hashed_pwd"


@pytest.mark.asyncio
async def test_create_user_duplicate_username_raises_conflict(
    user_service, mock_user_repository, mock_password_handler
):
    mock_password_handler.hash_password.return_value = "hashed_pwd"
    mock_user_repository.create = AsyncMock(side_effect=DuplicateKeyError("duplicate"))

    with pytest.raises(ConflictException, match="Username already exists"):
        await user_service.create_user("existinguser", "plain_pwd")


@pytest.mark.asyncio
async def test_update_user_success(user_service, mock_user_repository):
    updated_user = create_user_db(username="updateduser")
    user_update = UserUpdate(username="updateduser") # type: ignore
    mock_user_repository.update = AsyncMock(return_value=updated_user)

    result = await user_service.update_user("507f1f77bcf86cd799439011", user_update)

    assert result.id == "507f1f77bcf86cd799439011"
    assert result.username == "updateduser"
    mock_user_repository.update.assert_called_once_with(
        "507f1f77bcf86cd799439011", user_update
    )


@pytest.mark.asyncio
async def test_update_user_missing_raises_runtime_error(user_service, mock_user_repository):
    user_update = UserUpdate(username="updateduser") # type: ignore
    mock_user_repository.update = AsyncMock(return_value=None)

    with pytest.raises(RuntimeError, match="User missing after update - data integrity issue"):
        await user_service.update_user("missing_user", user_update)


@pytest.mark.asyncio
async def test_update_username_success(user_service, mock_user_repository):
    updated_user = create_user_db(username="renamed")
    mock_user_repository.update = AsyncMock(return_value=updated_user)

    result = await user_service.update_username("507f1f77bcf86cd799439011", "renamed")

    assert result is None
    updated_payload = mock_user_repository.update.call_args.args[1]
    assert isinstance(updated_payload, UserUpdate)
    assert updated_payload.username == "renamed"


@pytest.mark.asyncio
async def test_update_username_missing_raises_runtime_error(user_service, mock_user_repository):
    mock_user_repository.update = AsyncMock(return_value=None)

    with pytest.raises(RuntimeError, match="User missing after update - data integrity issue"):
        await user_service.update_username("missing_user", "renamed")


@pytest.mark.asyncio
async def test_change_password_success(
    user_service, mock_user_repository, mock_password_handler
):
    user_db = create_user_db(hash_password="old_hash")
    mock_user_repository.get_by_id = AsyncMock(return_value=user_db)
    mock_password_handler.verify_password.return_value = True
    mock_password_handler.hash_password.return_value = "new_hash"
    mock_user_repository.update = AsyncMock(return_value=create_user_db(hash_password="new_hash"))

    result = await user_service.change_password(
        "507f1f77bcf86cd799439011", "current_pwd", "new_pwd"
    )

    assert result is None
    mock_password_handler.verify_password.assert_called_once_with("current_pwd", "old_hash")
    mock_password_handler.hash_password.assert_called_once_with("new_pwd")

    updated_payload = mock_user_repository.update.call_args.args[1]
    assert isinstance(updated_payload, UserUpdate)
    assert updated_payload.hash_password == "new_hash"


@pytest.mark.asyncio
async def test_change_password_missing_user_raises_runtime_error(user_service, mock_user_repository):
    mock_user_repository.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(RuntimeError, match="User missing for password change"):
        await user_service.change_password("missing_user", "current_pwd", "new_pwd")


@pytest.mark.asyncio
async def test_change_password_wrong_current_password_raises_authentication_error(
    user_service, mock_user_repository, mock_password_handler
):
    user_db = create_user_db(hash_password="old_hash")
    mock_user_repository.get_by_id = AsyncMock(return_value=user_db)
    mock_password_handler.verify_password.return_value = False

    with pytest.raises(AuthenticationError, match="Current password is incorrect"):
        await user_service.change_password(
            "507f1f77bcf86cd799439011", "wrong_pwd", "new_pwd"
        )

    mock_user_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_change_password_update_failed_raises_runtime_error(
    user_service, mock_user_repository, mock_password_handler
):
    user_db = create_user_db(hash_password="old_hash")
    mock_user_repository.get_by_id = AsyncMock(return_value=user_db)
    mock_password_handler.verify_password.return_value = True
    mock_password_handler.hash_password.return_value = "new_hash"
    mock_user_repository.update = AsyncMock(return_value=None)

    with pytest.raises(RuntimeError, match="Password update failed"):
        await user_service.change_password(
            "507f1f77bcf86cd799439011", "current_pwd", "new_pwd"
        )


@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_user_repository):
    delete_result = MagicMock(deleted_count=1)
    mock_user_repository.delete = AsyncMock(return_value=delete_result)

    result = await user_service.delete_user("507f1f77bcf86cd799439011")

    assert result is None
    mock_user_repository.delete.assert_called_once_with("507f1f77bcf86cd799439011")


@pytest.mark.asyncio
async def test_delete_user_no_effect_raises_runtime_error(user_service, mock_user_repository):
    delete_result = MagicMock(deleted_count=0)
    mock_user_repository.delete = AsyncMock(return_value=delete_result)

    with pytest.raises(RuntimeError, match="Delete operation had no effect for user missing_user"):
        await user_service.delete_user("missing_user")


@pytest.mark.asyncio
async def test_get_by_username_found(user_service, mock_user_repository):
    user_db = create_user_db(username="testuser")
    mock_user_repository.get_by_username = AsyncMock(return_value=user_db)

    result = await user_service.get_by_username("testuser")

    assert result is not None
    assert result.username == "testuser"
    mock_user_repository.get_by_username.assert_called_once_with("testuser")


@pytest.mark.asyncio
async def test_get_by_username_not_found(user_service, mock_user_repository):
    mock_user_repository.get_by_username = AsyncMock(return_value=None)

    result = await user_service.get_by_username("unknown")

    assert result is None
    mock_user_repository.get_by_username.assert_called_once_with("unknown")


@pytest.mark.asyncio
async def test_get_by_id_found(user_service, mock_user_repository):
    user_db = create_user_db()
    mock_user_repository.get_by_id = AsyncMock(return_value=user_db)

    result = await user_service.get_by_id("507f1f77bcf86cd799439011")

    assert result is not None
    assert result.id == "507f1f77bcf86cd799439011"
    mock_user_repository.get_by_id.assert_called_once_with("507f1f77bcf86cd799439011")


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_service, mock_user_repository):
    mock_user_repository.get_by_id = AsyncMock(return_value=None)

    result = await user_service.get_by_id("missing_user")

    assert result is None
    mock_user_repository.get_by_id.assert_called_once_with("missing_user")


@pytest.mark.asyncio
async def test_verify_credentials_success(
    user_service, mock_user_repository, mock_password_handler
):
    user_db = create_user_db(username="verified_user", hash_password="stored_hash")
    mock_user_repository.get_by_username = AsyncMock(return_value=user_db)
    mock_password_handler.verify_password.return_value = True

    result = await user_service.verify_credentials("verified_user", "plain_pwd")

    assert result is not None
    assert result.id == "507f1f77bcf86cd799439011"
    assert result.username == "verified_user"
    mock_user_repository.get_by_username.assert_called_once_with("verified_user")
    mock_password_handler.verify_password.assert_called_once_with("plain_pwd", "stored_hash")


@pytest.mark.asyncio
async def test_verify_credentials_invalid_username_raises_authentication_error(
    user_service, mock_user_repository
):
    mock_user_repository.get_by_username = AsyncMock(return_value=None)

    with pytest.raises(AuthenticationError, match="Invalid username or password"):
        await user_service.verify_credentials("missing_user", "plain_pwd")


@pytest.mark.asyncio
async def test_verify_credentials_invalid_password_raises_authentication_error(
    user_service, mock_user_repository, mock_password_handler
):
    user_db = create_user_db(hash_password="stored_hash")
    mock_user_repository.get_by_username = AsyncMock(return_value=user_db)
    mock_password_handler.verify_password.return_value = False

    with pytest.raises(AuthenticationError, match="Invalid username or password"):
        await user_service.verify_credentials("testuser", "wrong_pwd")


@pytest.mark.asyncio
async def test_verify_credentials_repository_error_raises_runtime_error(
    user_service, mock_user_repository
):
    mock_user_repository.get_by_username = AsyncMock(side_effect=Exception("db down"))

    with pytest.raises(RuntimeError, match="Credential verification failed"):
        await user_service.verify_credentials("testuser", "plain_pwd")
