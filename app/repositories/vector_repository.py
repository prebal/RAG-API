from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
import torch

from app.models.vector_model import VectorEntry
from app.models.document_model import Document


class VectorRepository:
    def select_k_best_chunks(
        self, embedded_question: list, user_id, db: Session, top_k=5
    ):
        distances = VectorEntry.embedding.cosine_distance(embedded_question)

        query = (
            select(VectorEntry, distances.label("distance"))
            .join(Document)
            .where(Document.document_owner_id == user_id)
            .order_by(distances)
            .limit(top_k)
        )

        return db.execute(query).all()

    def create_vector(self, vectors_to_save: List[VectorEntry], db: Session) -> None:
        for vector_entry in vectors_to_save:
            db.add(vector_entry)

        db.commit()
