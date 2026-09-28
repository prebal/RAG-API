import asyncio
import hashlib
import logging
from datetime import UTC, datetime

from fastapi import HTTPException, UploadFile

from app.models.auth_model import User
from app.models.document_model import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.notebook_repository import NotebookRepository
from app.schemas.document_schema import DeleteDocumentRequest
from app.services.document_processor import DocumentProcessor
from app.services.storage_service import StorageService

SUPPORTED_FORMATS = ["pdf", "txt"]

service_logger = logging.getLogger("app")


class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        notebook_repository: NotebookRepository,
        storage_service: StorageService,
        document_processor: DocumentProcessor,
    ) -> None:

        self.document_repository = document_repository
        self.notebook_repository = notebook_repository
        self.storage_service = storage_service
        self.document_processor = document_processor

    def extract_metadata(self, uploaded_file: UploadFile) -> dict[str, int | str]:
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

    async def process_document(
        self,
        notebook_name: str,
        user: User,
        uploaded_file: UploadFile,
    ) -> None:
        service_logger.info(
            f"DocumentService.process_document: username={user.username}, "
            f"notebook_name={notebook_name}"
        )

        notebook_to_use = await self.notebook_repository.get_notebook_by_name(
            notebook_name, user.id
        )

        if notebook_to_use is None:
            raise HTTPException(
                400,
                detail="This notebook doesn't exist or you don't have the authorization to access it",
            )

        if uploaded_file.size == 0:
            raise HTTPException(400, detail="Uploaded file is empty")
        elif uploaded_file.size > 20e6:
            raise HTTPException(400, detail="Uploaded file is too large")

        document_hash = await self.generate_hash(uploaded_file)
        # Duplicate detection is per-notebook: the same file may exist in
        # different notebooks, but not twice inside the same one.
        document_hashes_per_notebook = (
            await self.document_repository.get_all_document_hashes_per_notebook(
                user.id, notebook_to_use.id
            )
        )

        if document_hash in document_hashes_per_notebook:
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
            notebook_assigned=notebook_to_use,
        )

        await self.document_repository.create_document(document_to_write)

        embedded_chunks = []
        embedded_chunks = await asyncio.to_thread(
            self.document_processor.embed_document, document_to_write
        )

        await self.document_processor.persist_chunks(document_to_write, embedded_chunks)

    async def remove_document(
        self, document_request: DeleteDocumentRequest, user_id: int
    ) -> None:
        service_logger.info(
            f"DocumentService.remove_document: user_id={user_id}, "
            f"document_id={document_request.document_id}, "
            f"notebook_name={document_request.notebook_name}"
        )

        notebook_to_use = await self.notebook_repository.get_notebook_by_name(
            document_request.notebook_name, user_id
        )
        if notebook_to_use is None:
            raise HTTPException(
                400,
                detail="This notebook doesn't exist or you don't have the authorization to access it",
            )

        filepath_to_remove = await self.document_repository.delete_document(
            document_request.document_id, user_id, notebook_to_use.id
        )
        self.storage_service.remove_document_storage(filepath_to_remove)

    async def get_document_per_notebook(self, notebook_name: str, user: User):
        queried_notebook = await self.notebook_repository.get_notebook_by_name(
            notebook_name, user.id
        )
        if queried_notebook is None:
            raise HTTPException(
                400,
                "The requested notebook doesn't exist or you don't have the authorization to access it",
            )

        return await self.document_repository.get_all_document_by_user_and_notebook(
            user.id, queried_notebook.id
        )
