from sqlalchemy import Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class VectorEntry(Base):
    __tablename__ = "vector_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    document_source: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE")
    )

    page_start: Mapped[int] = mapped_column(Integer)

    page_start: Mapped[int] = mapped_column(Integer)
