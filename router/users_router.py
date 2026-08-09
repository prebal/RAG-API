from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict

from models.auth_models import User
from dependencies import get_current_user
from schemas.user_schema import ChangeUsernameRequest, ChangePasswordRequest


user_router = APIRouter(prefix = "/user")

@user_router.get("/me")
def about_me(
        current_user: User =  Depends(get_current_user)
        ): -> User
    return current_user

@user_router.post("/delete_user")
def delete_user(
        current_user: User = Depends(get_current_user)
        ): -> Dict[str, str]

@user_router.post("/change_username")
def change_username(
        current_user: User = Depends(get_current_user),
        username_change_request: ChangeUsernameRequest
        ) -> Dict[str, str]:

@user_router.post("/change_password")
def change_password(
        current_user: User = Depends(get_current_user),
        password_change_request: ChangePasswordRequest
        ) -> Dict[str, str]:


