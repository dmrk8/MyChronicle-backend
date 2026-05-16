from fastapi import APIRouter, Depends, status

from app.auth.auth_dependencies import get_current_user
from app.models.db.user_models import (
    PasswordUpdateRequest,
    UserDB,
    UsernameUpdateRequest,
)
from app.services.user_service import UserService
from app.core.dependencies import get_user_service

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.patch("/me/username", status_code=status.HTTP_204_NO_CONTENT)
async def change_username(
    update_username: UsernameUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    await user_service.update_username(str(current_user.id), update_username)


@user_router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    update_password: PasswordUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    await user_service.change_password(
        str(current_user.id),
        update_password,
    )


@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    await user_service.delete_user(str(current_user.id))
