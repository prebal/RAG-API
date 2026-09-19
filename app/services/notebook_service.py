from app.services.document_services import DocumentService
from app.services.storage_service import StorageService
from fastapi import HTTPException

from app.models.auth_model import User
from app.models.notebook_model import Notebook
from app.schemas.notebook_schema import NotebookRequest
from app.repositories.notebook_repository import NotebookRepository


class NotebookService:
    def __init__(
        self, notebook_repository: NotebookRepository, storage_service: StorageService
    ) -> None:
        self.notebook_repository = notebook_repository
        self.storage_service = storage_service

    async def create_new_notebook(self, request: NotebookRequest, user: User) -> None:

        if (
            await self.notebook_repository.get_notebook_by_name(
                NotebookRequest.notebook_name, user.id
            )
        ) is not None:
            raise HTTPException()

        new_notebook = Notebook(
            notebook_name=NotebookRequest.notebook_name,
            notebook_owner=user,
            notebook_owner_id=user.id,
            created_at=datetime.now(UTC),
            last_accessed_at=datetime.now(UTC),
        )

        await self.notebook_repository.create_notebook(new_notebook)

    async def delete_notebook(self, request: NotebookRequest, user: User) -> None:
        # Delete Notebook instance requires:
        # Deleting notebook itself
        # Deleting conversations (cascades)
        # Deleting documents (cascades), orphaned docu<D-g>ments remain in storage

        notebook_from_db = await self.notebook_repository.get_notebook_by_name(
            NotebookRequest.notebook_name, user.id
        )

        if notebook_from_db is None:
            raise HTTPException()

        notebook_id = notebook_from_db.id

        documents_per_notebook = self.notebook_repository.get_all_document_by_user(
            user.id, notebook_id
        )

        for doc in documents_per_notebook:
            self.storage_service.remove_document_storage(doc.filepath)
        # Propagate manually because of local storage, MUST happen before deleting the
        # notebook to prevent the database entries in documents from being orphaned

        await self.notebook_repository.delete_notebook(notebook_id, user.id)
