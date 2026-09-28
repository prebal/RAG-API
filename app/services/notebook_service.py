import logging
from datetime import UTC, datetime

from fastapi import HTTPException

from app.models.auth_model import User
from app.models.notebook_model import Notebook
from app.repositories.document_repository import DocumentRepository
from app.repositories.notebook_repository import NotebookRepository
from app.schemas.notebook_schema import NotebookRequest
from app.services.storage_service import StorageService

service_logger = logging.getLogger("app")


class NotebookService:
    def __init__(
        self,
        notebook_repository: NotebookRepository,
        document_repository: DocumentRepository,
        storage_service: StorageService,
    ) -> None:
        self.notebook_repository = notebook_repository
        self.document_repository = document_repository
        self.storage_service = storage_service

    async def create_new_notebook(self, request: NotebookRequest, user: User) -> None:
        service_logger.info(
            f"NotebookService.create_new_notebook: username={user.username}, "
            f"notebook_name={request.notebook_name}"
        )

        existing_notebook = await self.notebook_repository.get_notebook_by_name(
            request.notebook_name, user.id
        )
        if existing_notebook is not None:
            raise HTTPException(
                status_code=409, detail="A notebook with this name already exists"
            )

        new_notebook = Notebook(
            notebook_name=request.notebook_name,
            notebook_owner=user,
            notebook_owner_id=user.id,
            created_at=datetime.now(UTC),
            last_accessed_at=datetime.now(UTC),
        )

        await self.notebook_repository.create_notebook(new_notebook)

    async def delete_notebook(self, request: NotebookRequest, user: User) -> None:
        service_logger.info(
            f"NotebookService.delete_notebook: username={user.username}, "
            f"notebook_name={request.notebook_name}"
        )

        notebook_from_db = await self.notebook_repository.get_notebook_by_name(
            request.notebook_name, user.id
        )

        if notebook_from_db is None:
            raise HTTPException(status_code=404, detail="Notebook not found")

        notebook_id = notebook_from_db.id

        documents_per_notebook = (
            await self.document_repository.get_all_document_by_user_and_notebook(
                user.id, notebook_id
            )
        )

        # Storage cleanup must happen before the row cascade fires
        # to prevent orphaned database entries in documents.
        for doc in documents_per_notebook:
            self.storage_service.remove_document_storage(doc.filepath)

        await self.notebook_repository.delete_notebook(notebook_id, user.id)

    async def get_all_notebooks(self, user: User):
        return await self.notebook_repository.get_all_notebooks_by_user(user.id)
