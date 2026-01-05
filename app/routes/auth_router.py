from typing import Optional
from fastapi import APIRouter, Cookie, Depends, Response, HTTPException
from app.models.auth_models import LoginRequest, UserInfo
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
    try:
        res = await auth_service.login(login_request)
        response.set_cookie(
            key="access_token",
            value=res.access_token,
            httponly=True,
            samesite="lax",
            secure=True,
            max_age=30 * 24 * 60 * 60,
        )

        return {"message": "login succesfull"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.post("/logout")
async def logout(
    response: Response,
    session_id: Optional[str] = Cookie(None),
):
    if session_id:

        try:
            response.delete_cookie(
                key="access_token", httponly=True, secure=True, samesite="lax"
            )
            return {"message": "Logged out successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.get("/me")
async def get_current_user_info(
    current_user: UserDB = Depends(get_current_user),
):
    try:
        return UserInfo(
            id=current_user.id,  # type: ignore
            username=current_user.username,
            role=current_user.role,
            createdAt=current_user.created_at,
            updatedAt=current_user.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.post("/refresh")
async def refresh_access_token(
    session_id: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not session_id:
        raise HTTPException(status_code=401, detail="No session found")

    try:
        res = await auth_service.refresh_access_token(session_id)
        return res.model_dump(exclude="session_id")
    except ValueError as ve:
        raise HTTPException(status_code=401, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
