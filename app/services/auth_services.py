import hashlib
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models.auth_model import User
from app.models.refresh_token_model import RefreshToken
from app.repositories.auth_repository import UserRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.auth_schema import RegisterRequest
from app.schemas.user_schema import (
    ChangePasswordRequest,
    ChangeUsernameRequest,
    DeleteUserRequest,
)
from app.security.jwt_tokens import (
    decode_jwt_token,
    issue_jwt_token,
    issue_refresh_token,
)
from app.security.password_hashing import hash_password, verify_password
from app.services.storage_service import StorageService


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        document_repository: DocumentRepository,
        storage_service: StorageService,
    ) -> None:
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.document_repository = document_repository
        self.storage_service = storage_service

    async def register_user(self, register_request: RegisterRequest) -> None:

        if (
            await self.user_repository.request_user_by_name(register_request.username)
            is not None
        ):
            raise HTTPException(
                status_code=409, detail="User with this username already exists"
            )

        if await self.user_repository.request_user_by_email(register_request.email):
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
        hashed_password = hash_password(register_request.password)

        new_user = User(
            username=register_request.username,
            email=register_request.email,
            password_hash=hashed_password,
            verified=False,
            date_added=datetime.now(UTC),
        )

        await self.user_repository.create_user(new_user)

    def generate_token_pair(self, user_id: int) -> tuple[str, str]:
        return (issue_jwt_token(user_id), issue_refresh_token(user_id))

    async def prepare_create_token_entry(
        self, user_id: int, refresh_token_str: str
    ) -> None:
        token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
        refresh_token_entry = RefreshToken(
            user_id=user_id,
            valid=True,
            token_hash=token_hash,
            expires_at=datetime.now(UTC) + timedelta(days=14),
        )

        await self.token_repository.create_token(refresh_token_entry)

    async def login_user(
        self, login_request: OAuth2PasswordRequestForm
    ) -> dict[str, str]:

        queried_user = await self.user_repository.request_user_by_name(
            login_request.username
        )

        if queried_user is None:
            raise HTTPException(status_code=401, detail="Incorrect login or password")

        if not verify_password(login_request.password, queried_user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect login or password")

        access_token, refresh_token = self.generate_token_pair(queried_user.id)

        await self.prepare_create_token_entry(queried_user.id, refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def token_rotation(self, old_refresh_token: str) -> dict[str, str]:
        decoded_old_refresh_token = decode_jwt_token(old_refresh_token)

        if decoded_old_refresh_token.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Not a refresh token")

        user_id = int(decoded_old_refresh_token["sub"])
        old_refresh_token_hash = hashlib.sha256(old_refresh_token.encode()).hexdigest()

        active_entry = await self.token_repository.find_active_token_by_hash(
            old_refresh_token_hash, user_id
        )
        if active_entry is None:
            raise HTTPException(
                status_code=401, detail="Refresh token revoked or unknown"
            )

        await self.token_repository.revoke_token(old_refresh_token_hash, user_id)

        new_access_token, new_refresh_token = self.generate_token_pair(user_id)

        await self.prepare_create_token_entry(user_id, new_refresh_token)

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}

    async def logout_user(self, refresh_token: str) -> None:
        decoded_refresh_token = decode_jwt_token(refresh_token)

        if decoded_refresh_token.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Not a refresh token")

        await self.token_repository.revoke_token(
            hashlib.sha256(refresh_token.encode()).hexdigest(),
            int(decoded_refresh_token["sub"]),
        )

    async def delete_user(self, delete_request: DeleteUserRequest, current_user: User):
        if not verify_password(delete_request.password, current_user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect password entered")

        all_documents = await self.document_repository.get_all_document_by_user(
            current_user.id
        )

        await self.user_repository.delete_user(current_user)

        for doc in all_documents:
            try:
                self.storage_service.remove_document_storage(doc.filepath)
            except FileNotFoundError:
                pass

    async def check_and_change_username(
        self,
        current_user: User,
        username_change_request: ChangeUsernameRequest,
    ) -> User | None:

        if not verify_password(
            username_change_request.password, current_user.password_hash
        ):
            raise HTTPException(status_code=401, detail="Incorrect login or password")

        if current_user.username == username_change_request.new_username:
            raise HTTPException(
                status_code=422, detail="Old and new usernames are identical"
            )

        return await self.user_repository.change_username(
            current_user, username_change_request.new_username
        )

    async def check_and_change_password(
        self,
        current_user: User,
        password_change_request: ChangePasswordRequest,
    ) -> User | None:

        if not verify_password(
            password_change_request.old_password, current_user.password_hash
        ):
            raise HTTPException(status_code=401, detail="Incorrect login or password")

        if verify_password(
            password_change_request.new_password, current_user.password_hash
        ):
            raise HTTPException(
                status_code=422, detail="Old and new passwords are identical"
            )

        new_password_hash = hash_password(password_change_request.new_password)

        updated_user = await self.user_repository.change_password(
            current_user, new_password_hash
        )

        await self.token_repository.revoke_all_for_user(current_user.id)

        return updated_user
