from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_model import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_document(self, document_id: int, user_id: int) -> Document | None:
        query = select(Document).where(
            Document.id == document_id, Document.document_owner_id == user_id
        )
        return await self.db.scalar(query)

    async def get_all_document_by_user(self, user_id: int):
        query = select(Document).where(Document.document_owner_id == user_id)

        return (await self.db.execute(query)).scalars().all()

    async def get_all_document_hashes(self, user_id):
        query = select(Document.document_hash).where(
            Document.document_owner_id == user_id
        )
        return (await self.db.execute(query)).scalars().all()

    async def delete_document(self, document_id: int, user_id: int) -> str:
        document_to_delete = await self.get_document(document_id, user_id)
        if document_to_delete is None:
            raise HTTPException(
                400,
                "You don't have authorization to delete document entry from database or the document doesn't exist",
            )

        document_to_delete_filepath = document_to_delete.filepath
        await self.db.delete(document_to_delete)
        await self.db.commit()
        return document_to_delete_filepath

    async def create_document(self, new_document: Document):
        self.db.add(new_document)
        await self.db.commit()
        await self.db.refresh(new_document)
