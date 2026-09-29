from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeleteDocumentRequest(BaseModel):
    document_id: int = Field()
    notebook_name: str = Field(max_length=255)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uploaded: datetime
    document_type: str
    document_size: int
