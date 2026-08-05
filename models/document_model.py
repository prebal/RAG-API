from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from models.base import Base
from models.auth_model import User

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    document_owner_id: Mapped[int] = mapped_column(Integer, ForeignKey(users.id, ondelete="CASCADE"))

    document_owner = relationship("User", backpopulates="documents")

    document_type: Mapped[str] = mapped_column(String, nullable = False, unique = False)

    uploaded: Mapped[datetime] = mapped_column(DateTime)

    filepath: Mapped[str] = mapped_column(String)
