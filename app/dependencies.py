from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.auth_repository import UserRepository
from app.security.jwt_tokens import decode_jwt_token

from app.repositories.auth_repository import UserRepository
from app.repositories.document_repository import DocumentRepository
from app.service.auth_services import UserService

oauth2_token_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_token_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
):
    decoded_jwt_token = decode_jwt_token(token)

    if not decoded_jwt_token["sub"]:
        raise HTTPException(401, "Invalid validation token. Please login again")

    queried_user = user_repository.request_user_by_id(int(decoded_jwt_token["sub"]))

    if queried_user is None:
        raise HTTPException(401, "Invalid user")

    return queried_user


def get_model_service(request: Request):
    return request.app.state.model_service


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(user_repository: Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)


def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)


def get_document_service(): ...


def get_storage_service(): ...
