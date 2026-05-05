from fastapi import Depends, Request
from app.core.exceptions import UnauthorizedException
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.db.user_models import User
from app.core.dependencies import get_auth_service, get_user_service
from structlog.contextvars import bind_contextvars


async def get_current_user(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """get current authenticated user"""

    token = request.cookies.get("access_token")

    if not token:
        raise UnauthorizedException(detail="Missing token")

    user_id = auth_service.verify_token(token)

    user = await user_service.get_by_id(user_id)
    if user is None:
        raise UnauthorizedException(detail="User no longer exists")

    bind_contextvars(user_id=user.id, role=user.role)
    return user
