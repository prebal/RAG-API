from fastapi import APIRouter, Depends, UploadFile
import uuid


from services.document_services import DocumentService
from services.storage import StorageService
from repositories.document_repository import DocumentRepository
from database import get_db

document_router = APIRouter(prefix = "/documents")
document_repository = DocumentRepository()
document_service = DocumentService(document_repository)
storage_service = StorageService()

@router.post("/upload_document")
async def add_document(
        current_user: Depends(get_current_user),
        db: Depends(get_db),
        uploaded_file: UploadFile
        ) -> Dict[str, str]:

    full_destination = storage_service.save_file(uploaded_file, destination)
    if full_destionation is None:
        raise HTTPException("500", "Internal server error occured while writing file")
    document_service.store_document_in_database(current_user, uploaded_file, full_destination, db)
    
    return {"message": "Document was added successfully"}
    
@router.post("/delete_document")
def delete_document(
        current_user: Depends(get_current_user),
        db: Depends(get_db),
        request: DeleteDocumentRequest
        ) -> None:
    
    
    document_filepath = document_service.(request.document_id)
    storage_service.delete_file(document_filepath)    

    


