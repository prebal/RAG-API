
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_model import Document
from app.models.vector_model import VectorEntry


class VectorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def select_k_best_chunks(self, embedded_question: list, user_id, top_k=5):
        distances = VectorEntry.embedding.cosine_distance(embedded_question)

        query = (
            select(VectorEntry, distances.label("distance"))
            .join(Document)
            .where(Document.document_owner_id == user_id)
            .order_by(distances)
            .limit(top_k)
        )

        return (await self.db.execute(query)).all()

    async def create_vector(self, vectors_to_save: list[VectorEntry]) -> None:
        for vector_entry in vectors_to_save:
            self.db.add(vector_entry)

        await self.db.commit()
