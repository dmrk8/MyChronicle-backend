from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user_service import UserService
from app.models.user_models import UserCreate, UserUpdateRequest, User
from app.core.dependencies import get_user_service
from app.auth.auth_dependencies import get_current_user

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@user_router.patch("/", response_model=User)
async def update_user(
    update_request: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return await user_service.update_user(current_user.id, update_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@user_router.delete("/", response_model=bool, status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return await user_service.delete_user(current_user.id) 
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
