from typing import Union

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_model import Document


class DocumentRepository():
    def get_document(self, document_id: int, user_id: int, db: Session) -> Union[Document, None]:
        query = select(Document).where(Document.id == document_id, Document.document_owner_id == user_id)
        return db.scalar(query)

    def delete_document(self, document_id: int, user_id: int, db: Session) -> str:
        document_to_delete = self.get_document(document_id, user_id, db)
        if document_to_delete is None:
            raise HTTPException(400, "You don't have authorization to delete document entry from database or the document doesn't exist")
        
        document_to_delete_filepath = document_to_delete.filepath
        db.delete(document_to_delete)
        db.commit()
        return document_to_delete_filepath

    def create_document(self, new_document: Document, db: Session):
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        
