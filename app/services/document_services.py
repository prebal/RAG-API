from datetime import UTC, datetime
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
import os
import hashlib

from app.models.auth_model import User
from app.models.document_model import Document
from app.services.document_processor import DocumentProcessor

SUPPORTED_FORMATS = ["pdf", "txt", "docx"]
document_processor = DocumentProcessor("sentence-transformers/all-MiniLM-L6-v2")


class DocumentService:
    def __init__(self, repository, storage_service):
        self.repository = repository
        self.storage_service = storage_service

    def extract_metadata(self, uploaded_file: UploadFile) -> Dict[str, Any]:
        metadata = {}
        metadata["size"] = uploaded_file.size
        metadata["file_format"] = str(uploaded_file.filename).split(".")[-1].lower()

        return metadata

    async def generate_hash(self, uploaded_file: UploadFile):
        sha256_hasher = hashlib.sha1()
        while chunk := await uploaded_file.read(1024**2):
            sha256_hasher.update(chunk)

        await uploaded_file.seek(0)
        return sha256_hasher.hexdigest()

    async def process_document(
        self, user: User, uploaded_file: UploadFile, db: Session
    ) -> None:

        document_hash = await self.generate_hash(uploaded_file)
        document_hashes_per_user = self.repository.get_all_document_hashes(user.id, db)

        if document_hash in document_hashes_per_user:
            raise HTTPException(status_code=422, detail="This document already exists")

        document_metadata = self.extract_metadata(uploaded_file)

        if document_metadata["file_format"] not in SUPPORTED_FORMATS:
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
            document_hash=document_hash,
            uploaded=datetime.now(UTC),
            filepath=full_filepath,
        )

        self.repository.create_document(document_to_write, db)

        document_processor.process_embed_document(document_to_write, db)

    def remove_document(self, document_id: int, user_id: int, db: Session):
        filepath_to_remove = self.repository.delete_document(document_id, user_id, db)
        self.storage_service.remove_document_storage(filepath_to_remove)
