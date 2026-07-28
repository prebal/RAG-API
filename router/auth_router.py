from services.auth_services import UserService
from repositories.auth_repository import UserRepository
from schemas.auth_schema import RegisterRequest, LoginRequest, LoginTokenResponse
from database import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix = "/auth")
repository = UserRepository()
service = UserService(repository)

@router.post("/register")
def register(
        request: RegisterRequest,
        db: Session = Depends(get_db)):

    service.register_user(request, db)

    return {"message": "Registration was successful"}

@router.post("/login")
def login(
        request: LoginRequest,
        db: Session = Depends(get_db)):

    issued_jwt_token = service.login_user(request, db)

    return LoginTokenResponse(
        token = issued_jwt_token,
        token_type = "bearer"
            )

    
