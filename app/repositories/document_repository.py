from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_model import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_document(
        self, document_id: int, user_id: int, notebook_id: int
    ) -> Document:
        query = select(Document).where(
            Document.id == document_id,
            Document.document_owner_id == user_id,
            Document.notebook_id == notebook_id,
        )

        db_results = await self.db.scalar(query)
        if db_results is None:
            raise HTTPException(
                400,
                "The document doesn't exist or you don't have the authorization to reach it",
            )

        return db_results

    async def get_all_document_by_user_and_notebook(
        self,
        user_id: int,
        notebook_id: int,
    ):
        query = select(Document).where(
            Document.document_owner_id == user_id, Document.notebook_id == notebook_id
        )

        return (await self.db.execute(query)).scalars().all()

    async def get_all_document_by_user(self, user_id: int):
        """All of a user's documents across every notebook.

        Used only by account deletion, which must wipe every file
        regardless of which notebook it sits in."""
        query = select(Document).where(Document.document_owner_id == user_id)
        return (await self.db.execute(query)).scalars().all()

    async def get_all_document_hashes_per_notebook(
        self, user_id: int, notebook_id: int
    ):
        query = select(Document.document_hash).where(
            Document.document_owner_id == user_id, Document.notebook_id == notebook_id
        )
        return (await self.db.execute(query)).scalars().all()

    async def delete_document(
        self, document_id: int, user_id: int, notebook_id: int
    ) -> str:
        document_to_delete = await self.get_document(document_id, user_id, notebook_id)
        document_to_delete_filepath = document_to_delete.filepath
        await self.db.delete(document_to_delete)
        await self.db.commit()
        return document_to_delete_filepath

    async def create_document(self, new_document: Document) -> None:
        self.db.add(new_document)
        await self.db.commit()
        await self.db.refresh(new_document)
