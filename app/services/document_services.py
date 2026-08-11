from datetime import UTC, datetime
from typing import dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
import os

from app.models.auth_model import User
from app.models.document_model import Document
from app.services.document_processor import DocumentProcessor

SUPPORTED_FORMATS = ["pdf", "txt", "docx"]


class DocumentService:
    def __init__(self, repository, storage_service):
        self.repository = repository
        self.storage_service = storage_service

    def extract_metadata(self, uploaded_file: UploadFile) -> dict[str, Any]:
        metadata = {}
        metadata["size"] = uploaded_file.size
        metadata["file_format"] = str(uploaded_file.filename).split(".")[-1]

        return metadata

    def process_document(
        self, user: User, uploaded_file: UploadFile, db: Session
    ) -> None:

        document_metadata = self.extract_metadata(uploaded_file)

        if document_metadata["file_format"].lower() not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=422, detail="Document of this type is not supported"
            )
        full_filepath = await self.storage_service.save_document_storage(uploaded_file)

        if not os.path.exists(full_filepath):
            raise HTTPException(
                status_code=500,
                detail="Internal server error occured while writing file",
            )

        document_to_write = Document(
            document_owner_id=user.id,
            document_owner=user,
            document_type=document_metadata["file_format"],
            document_size=document_metadata["size"],
            uploaded=datetime.now(UTC),
            filepath=full_filepath,
        )

        self.repository.create_document(document_to_write, db)

    def remove_document(self, document_id: int, user_id: int, db: Session):
        filepath_to_remove = self.repository.delete_document(document_id, user_id, db)
        self.storage_service.remove_document_storage(filepath_to_remove)
