import asyncio
import hashlib
import os
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, UploadFile

from app.models.auth_model import User
from app.models.document_model import Document

SUPPORTED_FORMATS = ["pdf", "txt", "docx"]


class DocumentService:
    def __init__(self, repository, storage_service, document_processor):
        self.repository = repository
        self.storage_service = storage_service
        self.document_processor = document_processor

    def extract_metadata(self, uploaded_file: UploadFile) -> dict[str, Any]:
        metadata = {}
        metadata["size"] = uploaded_file.size
        metadata["file_format"] = str(uploaded_file.filename).split(".")[-1].lower()

        return metadata

    async def generate_hash(self, uploaded_file: UploadFile):
        sha256_hasher = hashlib.sha256()
        while chunk := await uploaded_file.read(1024**2):
            sha256_hasher.update(chunk)

        await uploaded_file.seek(0)
        return str(sha256_hasher.hexdigest())

    async def process_document(self, user: User, uploaded_file: UploadFile) -> None:

        document_hash = await self.generate_hash(uploaded_file)
        document_hashes_per_user = await self.repository.get_all_document_hashes(
            user.id
        )

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

        await self.repository.create_document(document_to_write)

        embedded_chunks: list[dict] = []
        if document_to_write.document_type == "pdf":
            embedded_chunks = await asyncio.to_thread(
                self.document_processor.embed_pdf, document_to_write
            )

        await self.document_processor.persist_chunks(document_to_write, embedded_chunks)

    async def remove_document(self, document_id: int, user_id: int):
        filepath_to_remove = await self.repository.delete_document(document_id, user_id)
        self.storage_service.remove_document_storage(filepath_to_remove)
