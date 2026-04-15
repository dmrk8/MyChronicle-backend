from fastapi import APIRouter, Depends, status

from app.auth.auth_dependencies import get_current_user
from app.models.user_models import UpdatePassword, UpdateUsername, User
from app.services.user_service import UserService
from app.core.dependencies import get_user_service


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.patch("/username", status_code=status.HTTP_204_NO_CONTENT)
async def change_username(
    update_username: UpdateUsername,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return await user_service.update_username(current_user.id, update_username)


@user_router.patch("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: UpdatePassword,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    await user_service.change_password(
        current_user.id,
        payload.current_password,
        payload.new_password,
    )


@user_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    await user_service.delete_user(current_user.id)
