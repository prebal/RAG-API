from typing import Literal

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    question: str = Field()
    provider: Literal["local", "api"] = "local"
    notebook_name: str = Field(max_length=255)


class GetChatHistoryRequest(BaseModel):
    notebook_name: str = Field(max_length=255)
    # Let's assume the indexing starts from zero
    history_start: int
    history_end: int
