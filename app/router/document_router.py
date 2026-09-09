from fastapi import APIRouter, Depends, UploadFile

from app.dependencies import get_current_user, get_document_service
from app.models.auth_model import User
from app.services.document_services import DocumentService

document_router = APIRouter(prefix="/documents")


@document_router.post("/upload_document")
async def add_document(
    uploaded_file: UploadFile,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> dict[str, str]:

    await document_service.process_document(current_user, uploaded_file)
    return {"message": "Document was added successfully"}


@document_router.delete("/delete_document/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> dict[str, str]:

    await document_service.remove_document(document_id, current_user.id)
    return {"message": "Document was successfully removed"}
