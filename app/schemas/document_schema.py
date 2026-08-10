from pydantic import BaseModel, Field


class DeleteDocumentRequest(BaseModel):
    document_id: int = Field(default = None)
