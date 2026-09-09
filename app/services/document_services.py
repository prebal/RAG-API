import asyncio
import hashlib
from datetime import UTC, datetime
from typing import Dict

from fastapi import HTTPException, UploadFile

from app.models.auth_model import User
from app.models.document_model import Document

SUPPORTED_FORMATS = ["pdf", "txt", "docx"]


class DocumentService:
    def __init__(self, repository, storage_service, document_processor) -> None:
        self.repository = repository
        self.storage_service = storage_service
        self.document_processor = document_processor

    def extract_metadata(self, uploaded_file: UploadFile) -> Dict[str, int | str]:
        metadata = {}
        metadata["size"] = uploaded_file.size
        file_format = str(uploaded_file.filename).split(".")[-1].lower()
        if file_format == "txt" or file_format == "md":
            metadata["file_format"] = "txt"
        elif file_format == "pdf":
            metadata["file_format"] = "pdf"
        else:
            raise HTTPException(415, detail="Incorrect file format")
        return metadata

    async def generate_hash(self, uploaded_file: UploadFile) -> str:
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
                status_code=415, detail="Document of this type is not supported"
            )

        full_filepath = await self.storage_service.save_document_storage(uploaded_file)

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

        embedded_chunks = []
        embedded_chunks = await asyncio.to_thread(
            self.document_processor.embed_document, document_to_write
        )

        await self.document_processor.persist_chunks(document_to_write, embedded_chunks)

    async def remove_document(self, document_id: int, user_id: int) -> None:
        filepath_to_remove = await self.repository.delete_document(document_id, user_id)
        self.storage_service.remove_document_storage(filepath_to_remove)
