from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(max_length=30)
    password: str = Field(max_length=100)
    email: EmailStr = Field()


class LoginTokenResponse(BaseModel):
    access_token: str = Field()
    refresh_token: str = Field()
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field()
