from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Dict
import time
import logging
import uuid

from fastapi import FastAPI, Request

from app.database import async_engine
from app.router.auth_router import auth_router
from app.router.document_router import document_router
from app.router.llm_router import llm_router
from app.router.users_router import user_router
from app.services.model_service import ModelService
from app.logging import setup_logging, request_id_var


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    app.state.model_service = ModelService()
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(document_router)
app.include_router(llm_router)


@app.middleware("http")
async def logger_middleware(request: Request, call_next):
    arrival_time = time.perf_counter()
    try:
        request_id = request.headers["X-REQUEST-ID"]
    except KeyError:
        request_id = uuid.uuid4().hex[:12]

    request_id = request_id_var.set(request_id)
    response = await call_next(request)

    app_logger = logging.getLogger("app")
    app_logger.info(
        "http_request",
        extra={
            "http_method": request.method,
            "http_path": request.url.path,
            "status_code": response.status_code,
            "timestamp_arrival": arrival_time,
            "request_id": request_id_var.get(),
        },
    )

    return response


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "API is running"}
