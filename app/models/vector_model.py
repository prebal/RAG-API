from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class VectorEntry(Base):
    __tablename__ = "vector_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    document_source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE")
    )

    document_source = relationship("Document", back_populates="text_chunks")

    page_start: Mapped[int] = mapped_column(Integer)

    page_end: Mapped[int] = mapped_column(Integer)

    chunk_index: Mapped[int] = mapped_column(Integer)

    original_text: Mapped[str] = mapped_column(String)

    embedding = mapped_column(Vector(384))
