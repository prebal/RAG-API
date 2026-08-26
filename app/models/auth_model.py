from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    documents = relationship(
        "Document", back_populates="document_owner", cascade="all, delete-orphan"
    )

    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    password_hash: Mapped[str] = mapped_column(nullable=False)

    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    date_added: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    issued_refresh_tokens = relationship(
        "RefreshToken", back_populates="owner", cascade="all, delete-orphan"
    )
