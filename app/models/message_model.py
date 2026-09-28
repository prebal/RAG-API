from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    notebook_assigned_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("notebooks.id", ondelete="CASCADE"),
        nullable=False,
    )
    notebook_assigned = relationship("Notebook", back_populates="messages_assigned")

    message_owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    message_owner = relationship("User", back_populates="messages_written")

    role: Mapped[str] = mapped_column(String(50))

    content: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
