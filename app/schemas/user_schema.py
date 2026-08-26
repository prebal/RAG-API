from datetime import datetime

from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    old_password: str = Field()
    new_password: str = Field()


class ChangeUsernameRequest(BaseModel):
    new_username: str = Field()
    password: str = Field()


class DeleteUserRequest(BaseModel):
    password: str = Field()


class UserPublicResponse(BaseModel):
    id: int
    username: str
    email: str
    verified: bool
    date_added: datetime
