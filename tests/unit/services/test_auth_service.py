import pytest
from unittest.mock import AsyncMock, MagicMock

from app.auth.jwt_handler import JWTHandler
from app.core.exceptions import AuthenticationError, ConflictException
from app.models.auth_models import RegisterRequest
from app.models.user_models import User, UserRole
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from datetime import datetime, timezone


@pytest.fixture
def mock_jwt_handler():
    return MagicMock(spec=JWTHandler)


@pytest.fixture
def mock_user_service():
    return MagicMock(spec=UserService)


@pytest.fixture
def auth_service(mock_jwt_handler, mock_user_service):
    return AuthService(
        jwt_handler=mock_jwt_handler,
        user_service=mock_user_service,
    )


def create_user(user_id: str = "507f1f77bcf86cd799439011", username: str = "testuser") -> User:
    return User(
        id=user_id,
        username=username,
        role=UserRole.USER,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_register_success(auth_service, mock_jwt_handler, mock_user_service):
    register_request = RegisterRequest(username="newuser", password="SecurePass123!")
    created_user = create_user(username="newuser")
    mock_user_service.create_user = AsyncMock(return_value=created_user)
    mock_jwt_handler.create_access_token.return_value = "access_token_123"

    result = await auth_service.register(register_request)

    assert result == "access_token_123"
    mock_user_service.create_user.assert_called_once_with("newuser", "SecurePass123!")
    mock_jwt_handler.create_access_token.assert_called_once_with("507f1f77bcf86cd799439011")


@pytest.mark.asyncio
async def test_register_duplicate_username_raises_conflict(auth_service, mock_user_service):
    register_request = RegisterRequest(username="existinguser", password="SecurePass123!")
    mock_user_service.create_user = AsyncMock(side_effect=ConflictException("Username already exists"))

    with pytest.raises(ConflictException, match="Username already exists"):
        await auth_service.register(register_request)

    mock_user_service.create_user.assert_called_once_with("existinguser", "SecurePass123!")


@pytest.mark.asyncio
async def test_login_success(auth_service, mock_jwt_handler, mock_user_service):
    verified_user = create_user(username="testuser")
    mock_user_service.verify_credentials = AsyncMock(return_value=verified_user)
    mock_jwt_handler.create_access_token.return_value = "access_token_456"

    result = await auth_service.login("testuser", "correct_password")

    assert result == "access_token_456"
    mock_user_service.verify_credentials.assert_called_once_with("testuser", "correct_password")
    mock_jwt_handler.create_access_token.assert_called_once_with("507f1f77bcf86cd799439011")


@pytest.mark.asyncio
async def test_login_invalid_credentials_raises_authentication_error(auth_service, mock_user_service):
    mock_user_service.verify_credentials = AsyncMock(
        side_effect=AuthenticationError("Invalid username or password")
    )

    with pytest.raises(AuthenticationError, match="Invalid username or password"):
        await auth_service.login("testuser", "wrong_password")

    mock_user_service.verify_credentials.assert_called_once_with("testuser", "wrong_password")


@pytest.mark.asyncio
async def test_login_user_not_found_raises_authentication_error(auth_service, mock_user_service):
    mock_user_service.verify_credentials = AsyncMock(
        side_effect=AuthenticationError("Invalid username or password")
    )

    with pytest.raises(AuthenticationError, match="Invalid username or password"):
        await auth_service.login("nonexistent_user", "any_password")

    mock_user_service.verify_credentials.assert_called_once_with("nonexistent_user", "any_password")