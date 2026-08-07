from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from datetime import datetime, timezone
from typing import Dict

from models.auth_models import User
from models.document_model import Document
from schemas.document_schema import DeleteDocumentRequest
from repositories.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, repository):
        self.repository = repository

    def extract_metadata(self, uploaded_file: UploadFile) -> Dict[str, str]:
       pass 

    def save_document_db(self, 
                            user: User,
                            uploaded_file: UploadFile,
                            full_destination: str,
                            db: Session
                            ) -> None:

        #document_metadata = self.extract_metadata(uploaded_file)
        
        document_to_write = Document(
            document_owner_id = user.id,
            document_owner = user,
            document_type = "text",
            uploaded = datetime.now(timezone.utc),
            filepath = full_destination 
                )

        self.repository.create_document(document_to_write, db)

    def remove_document_db(self, document_id: int, user_id: int, db: Session):
        return self.repository.delete_document(document_id, user_id, db)
        

