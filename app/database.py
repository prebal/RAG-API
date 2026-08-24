import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base

load_dotenv()

_DATABASE_URL = f"postgresql+psycopg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:5432/notebook"

engine = create_engine(_DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush = False,
    autocommit = False
        )

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


async_engine = create_async_engine(_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
)


async def async_get_db() -> AsyncGenerator[AsyncSession]:
    db = AsyncSessionLocal()

    try:
        yield db
    finally:
        await db.close()
