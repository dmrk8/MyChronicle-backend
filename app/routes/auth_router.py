from fastapi import APIRouter, Depends, Response
from app.models.auth_models import LoginRequest
from app.services.auth_service import AuthService
from app.models.user_models import UserDB
from app.auth.auth_dependencies import get_current_user
from app.core.dependencies import get_auth_service

auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@auth_router.post("/login")
async def login(
    login_request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.login(login_request)
    
    response.set_cookie(
        key="access_token", value=result.access_token, httponly=True, samesite="lax", secure=True
    )

    return {"message": "Login successfull"}

@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@auth_router.get("/me")
async def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }
