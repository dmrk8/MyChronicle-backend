from fastapi import Depends, HTTPException, status, Request
from app.services.user_service import UserService
from app.models.user_models import UserDB, UserRole
from app.auth.jwt_handler import JWTHandler
from app.core.dependencies import get_user_service, get_jwt_handler


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

    username = jwt_handler.verify_token(token)

    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await user_service.get_by_username(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return user


async def require_admin(current_user: UserDB) -> UserDB:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
