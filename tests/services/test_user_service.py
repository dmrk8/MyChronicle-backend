import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pymongo.errors import DuplicateKeyError

from app.services.user_service import UserService
from app.models.db.user_models import (
    UserInsert,
    UserUpdate,
    User,
    UpdatePasswordRequest,
    UpdateUsernameRequest,
)
from app.core.exceptions import (
    AuthenticationError,
    ConflictException,
    NotFoundException,
)


@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.insert_user = AsyncMock()
    repo.update = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_username = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_password_handler():
    handler = MagicMock()
    handler.hash_password = MagicMock(return_value="hashed")
    handler.verify_password = MagicMock(return_value=True)
    return handler


@pytest.fixture
def user_service(mock_user_repo, mock_password_handler):
    return UserService(mock_user_repo, mock_password_handler)


@pytest.fixture
def user_insert():
    return UserInsert(username="testuser", hash_password="hashed")


@pytest.fixture
def user_db():
    user = MagicMock()
    user.username = "testuser"
    user.hash_password = "hashed"
    return user


@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_user_repo, user_insert, user_db):
    mock_user_repo.insert_user.return_value = user_db
    with patch("app.services.user_service.User.from_db", return_value="user_obj"):
        result = await user_service.create_user("testuser", "password")
    assert result == "user_obj"


@pytest.mark.asyncio
async def test_create_user_duplicate(user_service, mock_user_repo, user_insert):
    mock_user_repo.insert_user.side_effect = DuplicateKeyError("duplicate")
    with pytest.raises(ConflictException):
        await user_service.create_user("testuser", "password")


@pytest.mark.asyncio
async def test_update_username_success(user_service, mock_user_repo, user_db):
    mock_user_repo.update.return_value = user_db
    with patch("app.services.user_service.User.from_db", return_value="user_obj"):
        req = UpdateUsernameRequest(username="newname")
        result = await user_service.update_username("user_id", req)
    assert result == "user_obj"


@pytest.mark.asyncio
async def test_update_username_fail(user_service, mock_user_repo):
    mock_user_repo.update.return_value = None
    req = UpdateUsernameRequest(username="newname")
    with pytest.raises(
        RuntimeError, match="Unable to update username. Please try again later."
    ):
        await user_service.update_username("user_id", req)


@pytest.mark.asyncio
async def test_change_password_success(
    user_service, mock_user_repo, mock_password_handler, user_db
):
    mock_user_repo.get_by_id.return_value = user_db
    mock_password_handler.verify_password.return_value = True
    mock_password_handler.hash_password.return_value = "new_hash"
    mock_user_repo.update.return_value = user_db
    req = UpdatePasswordRequest(currentPassword="old", newPassword="NewPassword1*")
    with patch("app.services.user_service.User.from_db", return_value="user_obj"):
        result = await user_service.change_password("user_id", req)
    assert result == "user_obj"


@pytest.mark.asyncio
async def test_change_password_missing_user_raises_runtime_error(
    user_service, mock_user_repo
):
    mock_user_repo.get_by_id.return_value = None
    req = UpdatePasswordRequest(currentPassword="old", newPassword="NewPassword1*")
    with pytest.raises(
        RuntimeError, match="Unable to change password: Please try again later."
    ):
        await user_service.change_password("missing_user", req)


@pytest.mark.asyncio
async def test_change_password_wrong_current_password_raises_authentication_error(
    user_service, mock_user_repo, mock_password_handler, user_db
):
    mock_user_repo.get_by_id.return_value = user_db
    mock_password_handler.verify_password.return_value = False
    req = UpdatePasswordRequest(currentPassword="wrong", newPassword="NewPassword1*")
    with pytest.raises(AuthenticationError, match="Invalid Credentials"):
        await user_service.change_password("user_id", req)
    mock_user_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_change_password_update_failed_raises_runtime_error(
    user_service, mock_user_repo, mock_password_handler, user_db
):
    mock_user_repo.get_by_id.return_value = user_db
    mock_password_handler.verify_password.return_value = True
    mock_password_handler.hash_password.return_value = "new_hash"
    mock_user_repo.update.return_value = None
    req = UpdatePasswordRequest(currentPassword="old", newPassword="NewPassword1*")
    with pytest.raises(
        RuntimeError, match="Unable to change password. Please try again later."
    ):
        await user_service.change_password("user_id", req)


@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_user_repo):
    mock_user_repo.delete.return_value = True
    result = await user_service.delete_user("user_id")
    assert result is None
    mock_user_repo.delete.assert_called_once_with("user_id")


@pytest.mark.asyncio
async def test_delete_user_no_effect_raises_runtime_error(user_service, mock_user_repo):
    mock_user_repo.delete.return_value = False
    with pytest.raises(
        RuntimeError, match="Delete operation had no effect for user missing_user"
    ):
        await user_service.delete_user("missing_user")


@pytest.mark.asyncio
async def test_get_by_id_found(user_service, mock_user_repo, user_db):
    mock_user_repo.get_by_id.return_value = user_db
    with patch("app.services.user_service.User.from_db", return_value="user_obj"):
        result = await user_service.get_by_id("user_id")
    assert result == "user_obj"


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_service, mock_user_repo):
    mock_user_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundException):
        await user_service.get_by_id("missing_user")


@pytest.mark.asyncio
async def test_verify_credentials_success(
    user_service, mock_user_repo, mock_password_handler, user_db
):
    mock_user_repo.get_by_username.return_value = user_db
    mock_password_handler.verify_password.return_value = True
    with patch("app.services.user_service.User.from_db", return_value="user_obj"):
        result = await user_service.verify_credentials("testuser", "password")
    assert result == "user_obj"


@pytest.mark.asyncio
async def test_verify_credentials_invalid_username_raises_authentication_error(
    user_service, mock_user_repo
):
    mock_user_repo.get_by_username.return_value = None
    with pytest.raises(AuthenticationError, match="Invalid username or password"):
        await user_service.verify_credentials("missing_user", "plain_pwd")


@pytest.mark.asyncio
async def test_verify_credentials_invalid_password_raises_authentication_error(
    user_service, mock_user_repo, mock_password_handler, user_db
):
    mock_user_repo.get_by_username.return_value = user_db
    mock_password_handler.verify_password.return_value = False
    with pytest.raises(AuthenticationError, match="Invalid username or password"):
        await user_service.verify_credentials("testuser", "wrong_pwd")
