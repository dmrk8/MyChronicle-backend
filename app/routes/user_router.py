from fastapi import APIRouter, Depends, HTTPException, Path, status
from app.services.user_service import UserService
from app.models.user_models import UserCreate, UserUpdateRequest, UserResponse, UserDB
from app.core.dependencies import get_user_service
from app.auth.auth_dependencies import get_current_user, require_admin
from typing import Optional

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    try:
        return await user_service.create_user(user_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@user_router.patch("/", response_model=UserResponse)
async def update_user(
    update_request: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    try:
        return await user_service.update_user(current_user.id, update_request) # type: ignore
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@user_router.delete("/", response_model=UserResponse)
async def delete_user(
    user_service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    try:
        return await user_service.delete_user(current_user.id) # type: ignore
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@user_router.get("/{user_id}", response_model=Optional[UserDB])
async def get_user_by_id(
    user_id: str = Path(..., description="The ID of the user to retrieve"),
    user_service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    try:
        user = await user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
