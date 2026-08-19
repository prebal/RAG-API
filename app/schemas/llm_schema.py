from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    question: str = Field()
