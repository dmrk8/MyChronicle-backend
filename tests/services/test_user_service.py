import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.auth.password_handler import PasswordHandler
from app.models.user_models import UserCreate, UserUpdateRequest, UserDB, UserRole


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
    """Factory for UserDB instances with correct types."""
    defaults = {
        "id": "user_123",
        "username": "testuser",
        "hash_password": "hashed_pwd",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "role": UserRole.USER,
    }
    defaults.update(overrides)
    return UserDB(**defaults)


@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_user_repository, mock_password_handler):
    """Test successful user creation."""
    user_create = UserCreate(username="newuser", password="Secure@pass123")
    
    mock_user_repository.get_by_username = AsyncMock(return_value=None)
    mock_password_handler.hash_password = MagicMock(return_value="hashed_pwd")
    mock_user_repository.create = AsyncMock(return_value=MagicMock(
        inserted_id="user_456",
        acknowledged=True
    ))

    result = await user_service.create_user(user_create)

    assert result.id == "user_456"
    assert result.username == "newuser"
    assert result.role == UserRole.USER
    
    mock_password_handler.hash_password.assert_called_once_with("Secure@pass123")
    mock_user_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_already_exists(user_service, mock_user_repository):
    """Test creating user with existing username raises error."""
    user_create = UserCreate(username="existinguser", password="Passw@rd123")
    existing_user = create_user_db(username="existinguser")
    
    mock_user_repository.get_by_username = AsyncMock(return_value=existing_user)

    with pytest.raises(ValueError, match="Username already exists"):
        await user_service.create_user(user_create)


@pytest.mark.asyncio
async def test_update_user_not_found(user_service, mock_user_repository):
    """Test updating non-existent user raises error."""
    mock_user_repository.get_by_id = AsyncMock(return_value=None)
    update_request = UserUpdateRequest(username=None, password=None)

    with pytest.raises(ValueError, match="Cannot update nonexisting user"):
        await user_service.update_user("nonexistent_id", update_request)


@pytest.mark.asyncio
async def test_update_user_success(user_service, mock_user_repository):
    """Test successful user update."""
    existing_user = create_user_db()
    mock_user_repository.get_by_id = AsyncMock(return_value=existing_user)
    mock_user_repository.update = AsyncMock(return_value=MagicMock(
        matched_count=1,
        modified_count=1,
        acknowledged=True
    ))

    update_request = UserUpdateRequest(username="updateduser", password=None)
    result = await user_service.update_user("user_123", update_request)

    assert result.id == "user_123"
    assert result.username == "testuser"
    assert result.role == UserRole.USER
    mock_user_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service, mock_user_repository):
    """Test deleting non-existent user raises error."""
    mock_user_repository.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="User not found"):
        await user_service.delete_user("nonexistent_id")


@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_user_repository):
    """Test successful user deletion."""
    existing_user = create_user_db()
    mock_user_repository.get_by_id = AsyncMock(return_value=existing_user)
    mock_user_repository.delete = AsyncMock(return_value=MagicMock(
        deleted_count=1,
        acknowledged=True
    ))

    result = await user_service.delete_user("user_123")

    assert result is True
    mock_user_repository.delete.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_username_found(user_service, mock_user_repository):
    """Test getting user by username when user exists."""
    user = create_user_db(username="testuser")
    mock_user_repository.get_by_username = AsyncMock(return_value=user)

    result = await user_service.get_by_username("testuser")

    assert result is not None
    assert result.username == "testuser"
    mock_user_repository.get_by_username.assert_called_once_with("testuser")


@pytest.mark.asyncio
async def test_get_by_username_not_found(user_service, mock_user_repository):
    """Test getting user by username when user doesn't exist."""
    mock_user_repository.get_by_username = AsyncMock(return_value=None)

    result = await user_service.get_by_username("nonexistent")

    assert result is None


@pytest.mark.asyncio
async def test_get_by_id_found(user_service, mock_user_repository):
    """Test getting user by ID when user exists."""
    user = create_user_db()
    mock_user_repository.get_by_id = AsyncMock(return_value=user)

    result = await user_service.get_by_id("user_123")

    assert result is not None
    assert result.id == "user_123"


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_service, mock_user_repository):
    """Test getting user by ID when user doesn't exist."""
    mock_user_repository.get_by_id = AsyncMock(return_value=None)

    result = await user_service.get_by_id("nonexistent_id")

    assert result is None


@pytest.mark.asyncio
async def test_verify_credentials_invalid_username(user_service, mock_user_repository):
    """Test verifying credentials with non-existent username."""
    mock_user_repository.get_by_username = AsyncMock(return_value=None)

    result = await user_service.verify_credentials("nonexistent", "password")

    assert result is None


@pytest.mark.asyncio
async def test_verify_credentials_invalid_password(user_service, mock_user_repository, mock_password_handler):
    """Test verifying credentials with incorrect password."""
    user = create_user_db()
    mock_user_repository.get_by_username = AsyncMock(return_value=user)
    mock_password_handler.verify_password = MagicMock(return_value=False)

    result = await user_service.verify_credentials("testuser", "wrongpassword")

    assert result is None


@pytest.mark.asyncio
async def test_verify_credentials_success(user_service, mock_user_repository, mock_password_handler):
    """Test successful credential verification."""
    user = create_user_db()
    mock_user_repository.get_by_username = AsyncMock(return_value=user)
    mock_password_handler.verify_password = MagicMock(return_value=True)

    result = await user_service.verify_credentials("testuser", "correctpassword")

    assert result is not None
    assert result.id == "user_123"
    mock_password_handler.verify_password.assert_called_once()
