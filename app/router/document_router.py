from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile

from app.dependencies import get_current_user, get_document_service
from app.models.auth_model import User
from app.schemas.document_schema import DeleteDocumentRequest, DocumentResponse
from app.services.document_services import DocumentService

document_router = APIRouter(prefix="/documents")


@document_router.post("/upload_document")
async def add_document(
    uploaded_file: UploadFile,
    notebook_name: Annotated[str, Form()],
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> dict[str, str]:

    await document_service.process_document(notebook_name, current_user, uploaded_file)
    return {"message": "Document was added successfully"}


@document_router.delete("/delete_document")
async def delete_document(
    document_request: DeleteDocumentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> dict[str, str]:

    await document_service.remove_document(document_request, current_user.id)
    return {"message": "Document was successfully removed"}


@document_router.get(
    "/get_documents_by_notebook", response_model=list[DocumentResponse]
)
async def get_documents_by_notebook(
    notebook_name: str,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentResponse]:
    return await document_service.get_document_per_notebook(notebook_name, current_user)
