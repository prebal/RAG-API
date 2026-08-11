from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    document_owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )

    document_owner = relationship("User", back_populates="documents")

    document_type: Mapped[str] = mapped_column(String, nullable=False, unique=False)

    document_size: Mapped[int] = mapped_column(Integer, nullable=False, unique=False)

    uploaded: Mapped[datetime] = mapped_column(DateTime)

    filepath: Mapped[str] = mapped_column(String)
