from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    old_password: str = Field()
    new_password: str = Field()

class ChangeUsernameRequest(BaseModel):
    new_username: str = Field()
    password: str = Field()


