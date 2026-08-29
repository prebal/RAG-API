from pydantic import BaseModel, Field


# Scheduled for deletion maybe
class DeleteDocumentRequest(BaseModel):
    document_id: int = Field()
