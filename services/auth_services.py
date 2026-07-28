from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from security.password_hashing import hash_password, verify_password
from security.jwt_tokens import issue_jwt_token
from schemas.auth_schema import RegisterRequest, LoginRequest
from models.auth_models import User
from repositories.auth_repository import UserRepository



class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def register_user(self, register_request: RegisterRequest, db: Session) -> None:

        if self.repository.request_user_by_name(register_request.login_name, db):
            # TODO: This function returns either None or User. Make some logic around it for validation later 
            raise Error()

        if self.repository.request_user_by_email(register_request.email, db):
            raise Error()

        hashed_password = hash_password(register_request.password)


        new_user = User(
                login_name = register_request.login_name,
                email = register_request.email,
                password_hash = hashed_password,
                verified = False,
                date_added = datetime.now(timezone.utc)
                )

        self.repository.create_user(new_user, db)

        
    def login_user(self, login_request: LoginRequest, db: Session) -> None:

        queried_user = self.repository.request_user_by_name(login_request.login_name, db)
            
        if not queried_user:
            raise HTTPException(status_code = 401, detail="Incorrect login or password")

        if not verify_password(login_request.password, queried_user.password_hash):
            raise HTTPException(status_code = 401, detail="Incorrect login or password")
       
        return issue_jwt_token(queried_user.id)

