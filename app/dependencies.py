from functools import lru_cache

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_get_db
from app.models.auth_model import User
from app.repositories.auth_repository import UserRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.vector_repository import VectorRepository
from app.schemas.llm_schema import LLMRequest
from app.security.jwt_tokens import decode_jwt_token
from app.services.auth_services import UserService
from app.services.document_processor import DocumentProcessor
from app.services.document_services import DocumentService
from app.services.llm_service import LLMService
from app.services.model_service import ModelService
from app.services.storage_service import StorageService
from app.settings import get_settings

oauth2_token_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Model related service
def get_model_service(request: Request) -> ModelService:
    return request.app.state.model_service


# User and auth related services and repositories
def get_user_repository(db: AsyncSession = Depends(async_get_db)) -> UserRepository:
    return UserRepository(db)


def get_token_repository(db: AsyncSession = Depends(async_get_db)) -> TokenRepository:
    return TokenRepository(db)


# Document related services
def get_document_repository(
    db: AsyncSession = Depends(async_get_db),
) -> DocumentRepository:
    return DocumentRepository(db)


def get_vector_repository(db: AsyncSession = Depends(async_get_db)) -> VectorRepository:
    return VectorRepository(db)


def get_storage_service() -> StorageService:
    return StorageService()


# Assembled auth service (all dependencies defined above — Depends resolves at def time)
def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    token_repository: TokenRepository = Depends(get_token_repository),
    document_repository: DocumentRepository = Depends(get_document_repository),
    storage_service: StorageService = Depends(get_storage_service),
) -> UserService:
    return UserService(
        user_repository, token_repository, document_repository, storage_service
    )


def get_document_processor(
    model_service: ModelService = Depends(get_model_service),
    vector_repository: VectorRepository = Depends(get_vector_repository),
) -> DocumentProcessor:
    return DocumentProcessor(model_service, vector_repository)


def get_document_service(
    document_repository: DocumentRepository = Depends(get_document_repository),
    storage_service: StorageService = Depends(get_storage_service),
    document_processor: DocumentProcessor = Depends(get_document_processor),
) -> DocumentService:
    return DocumentService(document_repository, storage_service, document_processor)


# Authenticated user resolution
async def get_current_user(
    token: str = Depends(oauth2_token_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    decoded_jwt_token = decode_jwt_token(token)
    if decoded_jwt_token["type"] != "access":
        raise HTTPException(401, "Incorrect validation token supplied.")

    if not decoded_jwt_token["sub"]:
        raise HTTPException(401, "Invalid validation token. Please login again")

    queried_user = await user_repository.request_user_by_id(
        int(decoded_jwt_token["sub"])
    )

    if queried_user is None:
        raise HTTPException(401, "Invalid user")

    return queried_user


# LLM services
@lru_cache
def get_llm_clients() -> dict[str, tuple[AsyncOpenAI, str]]:
    """Process-wide singleton of LLM clients.

    Clients are stateless and expensive (HTTP connection pools) -> built once,
    shared by all requests. DB-bound repositories must NOT live here: they wrap
    a request-scoped Session and are assembled per request in get_llm_service.
    """
    settings = get_settings()
    clients = {
        "local": (
            AsyncOpenAI(
                base_url=settings.llm_local_base_url,
                api_key="ollama",
            ),
            settings.llm_local_model,
        )
    }

    if settings.llm_api_key:
        clients["api"] = (
            AsyncOpenAI(
                base_url=settings.llm_api_base_url or None,
                api_key=settings.llm_api_key,
            ),
            settings.llm_api_model,
        )

    return clients


def get_llm_service(
    llm_request: LLMRequest,
    clients: dict[str, tuple[AsyncOpenAI, str]] = Depends(get_llm_clients),
    model_service: ModelService = Depends(get_model_service),
    vector_repository: VectorRepository = Depends(get_vector_repository),
) -> LLMService:
    entry = clients.get(llm_request.provider)
    if entry is None:
        raise HTTPException(
            503, f"LLM provider '{llm_request.provider}' is not configured"
        )

    client, model_name = entry
    return LLMService(
        client=client,
        model_name=model_name,
        model_service=model_service,
        vector_repository=vector_repository,
    )
