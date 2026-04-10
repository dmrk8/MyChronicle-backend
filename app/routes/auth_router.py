from fastapi import APIRouter, Body, Depends, Response, HTTPException
from app.models.auth_models import RegisterRequest
from app.services.auth_service import AuthService
from app.models.user_models import User
from app.auth.auth_dependencies import get_current_user
from app.core.dependencies import get_auth_service
from app.core.config import get_settings

auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@auth_router.post("/register")
async def register(
    register_request: RegisterRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token = await auth_service.register(register_request)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite=get_settings().samesite,
        secure=True,
        max_age=30 * 24 * 60 * 60,
    )


@auth_router.post("/login")
async def login(
    response: Response,
    username: str = Body(...),
    password: str = Body(...),
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token = await auth_service.login(username, password)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite=get_settings().samesite,
        secure=True,
        max_age=30 * 24 * 60 * 60,
    )


@auth_router.post("/logout")
async def logout(
    response: Response,
):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite=get_settings().samesite,
    )


@auth_router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return current_user
