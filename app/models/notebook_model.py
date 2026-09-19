from datetime import UTC, datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column, ForeignKey

from app.models.base import Base


class Notebook(Base):
    __tablename__ = "notebooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    notebook_owner = relationship("User", back_populates="notebooks_owned")

    documents_saved = relationship(
        "Document", back_populates="notebook_assigned", cascade="all, delete-orphan"
    )

    conversations = relationship(
        "Conversation",
        back_populates="notebook_conversation_run_in",
        cascade="all, delete-orphan",
    )

    notebook_name: Mapped[str] = mapped_column(String, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    last_accessed_at: Mapped[datetime] = mapped_column(DateTime)
