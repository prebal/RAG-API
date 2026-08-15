from datetime import UTC, datetime

from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.auth_model import User
from app.repositories.auth_repository import UserRepository
from app.schemas.auth_schema import RegisterRequest
from app.schemas.user_schema import ChangePasswordRequest, ChangeUsernameRequest
from app.security.jwt_tokens import issue_jwt_token
from app.security.password_hashing import hash_password, verify_password


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def register_user(self, register_request: RegisterRequest, db: Session) -> None:

        if (
            self.repository.request_user_by_name(register_request.username, db)
            is not None
        ):
            # TODO: This function returns either None or User. Make some logic around it for validation later
            raise HTTPException(
                status_code=409, message="User with this username already exists"
            )

        if self.repository.request_user_by_email(register_request.email, db):
            raise HTTPException(
                status_code=409, message="User who uses this email already exists"
            )
        hashed_password = hash_password(register_request.password)

        new_user = User(
            username=register_request.username,
            email=register_request.email,
            password_hash=hashed_password,
            verified=False,
            date_added=datetime.now(UTC),
        )

        self.repository.create_user(new_user, db)

    def login_user(self, login_request: LoginRequest, db: Session) -> str:

        queried_user = self.repository.request_user_by_name(login_request.username, db)

        if queried_user is None:
            raise HTTPException(status_code=401, detail="Incorrect login or password")

        if not verify_password(login_request.password, queried_user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect login or password")

        return issue_jwt_token(queried_user.id)

    def check_and_change_username(
        self,
        current_user: User,
        username_change_request: ChangeUsernameRequest,
        db: Session,
    ) -> User | None:

        if not verify_password(
            username_change_request.password, current_user.password_hash
        ):
            raise HTTPException(status_code=401, detail="Incorrect login or password")

        if current_user.username == username_change_request.new_username:
            raise HTTPException(
                status_code=422, detail="Old and new usernames are identical"
            )

        return self.repository.change_username(
            current_user, username_change_request.new_username, db
        )

    def check_and_change_password(
        self,
        current_user: User,
        password_change_request: ChangePasswordRequest,
        db: Session,
    ) -> User | None:

        if not verify_password(
            password_change_request.old_password, current_user.password_hash
        ):
            raise HTTPException(status_code=401, detail="Incorrect login or password")

        try:
            verify_password(
                password_change_request.new_password, current_user.password_hash
            )
        except VerifyMismatchError:
            pass
        else:
            raise HTTPException(
                status_code=422, detail="Old and new passwords are identical"
            )

        new_password_hash = hash_password(password_change_request.new_password)

        return self.repository.change_password(current_user, new_password_hash, db)
