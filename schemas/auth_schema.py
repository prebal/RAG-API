from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str = Field(default = None, max_lenght = 50)
    password: str = Field(default = None, max_length = 100)

class RegisterRequest(BaseModel):
    username: str = Field(default = None, max_length = 50)
    password: str = Field(default = None, max_length = 100)
    email: str = Field()

class LoginTokenResponse(BaseModel):
    access_token: str = Field(default = None)
    token_type: str = Field(default = None)
