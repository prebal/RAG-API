from datetime import datetime

from app.models.base import Base
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    documents = relationship("Document", back_populates="document_owner")

    username: Mapped[str] = mapped_column(String(30), nullable = False, unique = True)

    email: Mapped[str] = mapped_column(String(255), nullable = False, unique = True)

    password_hash: Mapped[str] = mapped_column(nullable = False, unique = True)

    verified: Mapped[bool] = mapped_column(Boolean, nullable = False, unique = False, default = False)

    date_added: Mapped[datetime] = mapped_column(DateTime)


