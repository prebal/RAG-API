from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.auth_repository import UserRepository
from app.schemas.auth_schema import LoginTokenResponse, RegisterRequest
from app.services.auth_services import UserService

router = APIRouter(prefix="/auth")
repository = UserRepository()
service = UserService(repository)


@router.post("/register")
def register(request: RegisterRequest):

    service.register_user(request)

    return {"message": "Registration was successful"}


@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends()):

    issued_jwt_token = service.login_user(request)

    return LoginTokenResponse(access_token=issued_jwt_token, token_type="bearer")
