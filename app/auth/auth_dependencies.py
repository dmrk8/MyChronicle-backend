from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt_handler import verify_token
from app.services.user_service import UserService
from app.models.user_models import UserData, UserRole

security = HTTPBearer()
user_service = UserService()

async def get_current_user(request: Request) -> UserData:
    """get current authenticated user"""

    token = request.cookies.get("access_token")

    if not token:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="could not validate credentials",
            headers={"WWW-Authenticate" : "Bearer"}
        )
        
    username = verify_token(token)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = user_service.get_by_username(username)
    if user is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return user

async def require_admin(current_user: UserData = Depends(get_current_user)) -> UserData:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user