from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_user_service
from app.models.auth_model import User
from app.schemas.user_schema import (
    ChangePasswordRequest,
    ChangeUsernameRequest,
    DeleteUserRequest,
    UserPublicResponse,
)
from app.services.auth_services import UserService

user_router = APIRouter(prefix="/user")


@user_router.get("/me", response_model=UserPublicResponse)
def about_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@user_router.delete("/delete_user")
async def delete_user(
    delete_user_request: DeleteUserRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> dict[str, str]:

    await user_service.delete_user(delete_user_request, current_user)

    return {"message": "User account was deleted"}


@user_router.post("/change_username")
async def change_username(
    username_change_request: ChangeUsernameRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> dict[str, str]:

    await service.check_and_change_username(current_user, username_change_request)

    return {"message": "Username change was successful"}


@user_router.post("/change_password")
async def change_password(
    password_change_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> dict[str, str]:

    await service.check_and_change_password(current_user, password_change_request)

    return {"message": "Password change was successful"}
