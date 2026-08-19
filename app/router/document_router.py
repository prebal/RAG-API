from fastapi import APIRouter, Depends, UploadFile
from typing import Dict

from app.database import get_db
from app.dependencies import get_current_user
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_schema import DeleteDocumentRequest
from app.services.document_services import DocumentService
from app.services.storage_service import StorageService

document_router = APIRouter(prefix="/documents")
document_repository = DocumentRepository()
storage_service = StorageService()
document_service = DocumentService(document_repository, storage_service)


@document_router.post("/upload_document")
async def add_document(
    uploaded_file: UploadFile,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
) -> Dict[str, str]:

    await document_service.process_document(current_user, uploaded_file, db)
    return {"message": "Document was added successfully"}


@document_router.post("/delete_document")
def delete_document(
    request: DeleteDocumentRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
) -> Dict[str, str]:

    document_service.remove_document(request.document_id, current_user.id, db)
    return {"message": "Document was successfully removed"}
