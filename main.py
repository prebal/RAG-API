from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI

from app.database import async_engine
from app.router.auth_router import auth_router
from app.router.document_router import document_router
from app.router.llm_router import llm_router
from app.router.users_router import user_router
from app.services.model_service import ModelService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.model_service = ModelService()
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(document_router)
app.include_router(llm_router)


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "API is running"}
