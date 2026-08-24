from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.auth_model import User
from app.repositories.auth_repository import UserRepository
from app.schemas.user_schema import ChangePasswordRequest, ChangeUsernameRequest
from app.services.auth_services import UserService

user_router = APIRouter(prefix="/user")
auth_repository = UserRepository()
auth_service = UserService(auth_repository)


@user_router.get("/me", response_model=None)
def about_me(current_user: User = Depends(get_current_user)) -> User:
    current_user.password_hash = "REDACTED"
    return current_user


@user_router.post("/delete_user")
def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:

    raise NotImplementedError


@user_router.post("/change_username")
def change_username(
    username_change_request: ChangeUsernameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:

    auth_service.check_and_change_username(current_user, username_change_request, db)

    return {"message": "Username change was successful"}


@user_router.post("/change_password")
def change_password(
    password_change_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:

    auth_service.check_and_change_password(current_user, password_change_request, db)

    return {"message": "Password change was successful"}
