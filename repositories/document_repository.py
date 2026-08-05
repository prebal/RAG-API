from sqlaclhemy import select
from sqlalchemy.orm import Session
from models.document_model import Document
from typing import Union

class DocumentRepository():
    def get_document(self, document_id: int, user_id: int, db: Session) -> Union[Document, None]:
        query = db.select(Document).where(Document.id == document_id, Document.document_owner_id == user_id)


    def delete_document(self, document_id: int, user_id: int, db: Session) -> None:
        document_to_delete = self.get_document(document_id, user_id)
        if document_to_delete is None:
            raise HTTPException("400", "You don't have authorization to delete document entry from database or the document doesn't exist")

        db.delete(document_to_delete)
        db.commit()


    def create_document(self, new_document: Document, db: Session):
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        
