from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )

    owner = relationship("User", back_populates="issued_refresh_tokens")

    valid: Mapped[bool] = mapped_column(Boolean, default=True)

    token_hash: Mapped[str] = mapped_column(String, unique=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime)
