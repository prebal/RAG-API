from pydantic import BaseModel, Field


# For now, this schema is used by both add and remove notebook.
# Realistically, once each request needs separate schema, it wil be implemented
class NotebookRequest(BaseModel):
    notebook_name: str = Field()
