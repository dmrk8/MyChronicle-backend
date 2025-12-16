from fastapi import Depends, HTTPException, status, Request
from app.services.user_service import UserService
from app.models.user_models import UserDB, UserRole
from app.auth.jwt_handler import JWTHandler
from app.core.dependencies import get_user_service, get_jwt_handler
from structlog.contextvars import bind_contextvars


async def get_current_user(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
) -> UserDB:
    """get current authenticated user"""

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = jwt_handler.verify_token(token)

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    bind_contextvars(
        user_id=user.id,
        role=user.role
    )
    
    return user


async def require_admin(current_user: UserDB) -> UserDB:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
