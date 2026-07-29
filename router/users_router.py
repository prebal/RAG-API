from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.auth_models import User
from dependencies import get_current_user

user_router = APIRouter(prefix = "/user")

@user_router.post("/me")
def about_me(
        current_user: User =  Depends(get_current_user)
        ):
    return current_user
