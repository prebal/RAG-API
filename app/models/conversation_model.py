from app.models.notebooks import mapped_column
from sqlalchemy import Integer, String, DateTime

from app.models.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    conversation_owner = relationship("User", back_populates="conversations_of_user")

    notebook_conversation_run_in = relationship(
        "Notebook", back_populates="conversations"
    )

    conversation_name: Mapped[str] = mapped_column(String, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    last_accessed_at: Mapped[datetime] = mapped_column(DateTime)
