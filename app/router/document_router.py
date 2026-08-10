import uuid
from typing import Dict

from fastapi import APIRouter, Depends, UploadFile

from app.database import get_db
from app.dependencies import get_current_user
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_schema import DeleteDocumentRequest
from app.services.document_services import DocumentService
from app.services.storage_service import StorageService

document_router = APIRouter(prefix = "/documents")
document_repository = DocumentRepository()
document_service = DocumentService(document_repository)
storage_service = StorageService()

@document_router.post("/upload_document")
async def add_document(
        uploaded_file: UploadFile,
        current_user = Depends(get_current_user),
        db = Depends(get_db),
        ) -> Dict[str, str]:

    full_destination = await storage_service.save_document_storage(uploaded_file)
    if full_destination is None:
        raise HTTPException("500", "Internal server error occured while writing file")
    document_service.save_document_db(current_user, uploaded_file, full_destination, db)
    
    return {"message": "Document was added successfully"}
    
@document_router.post("/delete_document")
def delete_document(
        request: DeleteDocumentRequest,
        current_user = Depends(get_current_user),
        db = Depends(get_db),
        ) -> None:
    
    
    document_filepath = document_service.remove_document_db(request.document_id, current_user.id, db)
    storage_service.remove_document_storage(document_filepath)    

    


