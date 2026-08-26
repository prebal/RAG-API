from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import get_user_service
from app.schemas.auth_schema import LoginTokenResponse, RefreshRequest, RegisterRequest
from app.services.auth_services import UserService

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register")
async def register(
    request: RegisterRequest, service: UserService = Depends(get_user_service)
):
    await service.register_user(request)

    return {"message": "Registration was successful"}


@auth_router.post("/login", response_model=LoginTokenResponse)
async def login(
    request: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    return LoginTokenResponse(**await service.login_user(request))


@auth_router.post("/refresh", response_model=LoginTokenResponse)
async def refresh(
    request: RefreshRequest, service: UserService = Depends(get_user_service)
):
    return LoginTokenResponse(**await service.token_rotation(request.refresh_token))


@auth_router.post("/logout")
async def logout(
    request: RefreshRequest, service: UserService = Depends(get_user_service)
):
    await service.logout_user(request.refresh_token)

    return {"message": "Logged out successfully"}
