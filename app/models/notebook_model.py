from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Notebook(Base):
    __tablename__ = "notebooks"
    __table_args__ = (
        UniqueConstraint(
            "notebook_owner_id", "notebook_name", name="uq_notebook_owner_name"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    notebook_owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    notebook_owner = relationship("User", back_populates="notebooks_owned")

    documents_saved = relationship(
        "Document", back_populates="notebook_assigned", cascade="all, delete-orphan"
    )

    notebook_name: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    messages_assigned = relationship(
        "Message", back_populates="notebook_assigned", cascade="all, delete-orphan"
    )

    last_accessed_at: Mapped[datetime] = mapped_column(DateTime)
