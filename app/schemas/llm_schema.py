from typing import Literal

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    question: str = Field()
    provider: Literal["local", "api"] = "local"
