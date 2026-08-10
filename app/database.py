import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base

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
