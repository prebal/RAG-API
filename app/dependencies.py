from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.auth_repository import UserRepository
from app.security.jwt_tokens import decode_jwt_token

oauth2_token_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_token_scheme), db: Session = Depends(get_db)
):
    decoded_jwt_token = decode_jwt_token(token)

    if not decoded_jwt_token["sub"]:
        raise HTTPException(401, "Invalid validation token. Please login again")

    queried_user = UserRepository().request_user_by_id(
        int(decoded_jwt_token["sub"]), db
    )

    if queried_user is None:
        raise HTTPException(401, "Invalid user")

    return queried_user
