from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# For now, this schema is used by both add and remove notebook.
# Realistically, once each request needs separate schema, it wil be implemented
class NotebookRequest(BaseModel):
    notebook_name: str = Field()


class NotebookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    notebook_name: str
    created_at: datetime
    last_accessed_at: datetime
