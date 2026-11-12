from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import (
    get_current_user,
    get_llm_service,
    get_message_repository,
    get_notebook_repository,
)
from app.models.auth_model import User
from app.repositories.messages_repository import MessageRepository
from app.repositories.notebook_repository import NotebookRepository
from app.schemas.llm_schema import GetChatHistoryRequest, LLMRequest
from app.services import llm_service
from app.services.llm_service import LLMService

llm_router = APIRouter(prefix="/llm")


@llm_router.post("/ask_question")
async def ask_question(
    llm_request: LLMRequest,
    llm_service: Annotated[LLMService, Depends(get_llm_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StreamingResponse:
    return StreamingResponse(
        llm_service.generate_response(llm_request, current_user),
        media_type="text/event-stream",
    )


@llm_router.post("/get_chat_history")
async def get_chat_history(
    chat_history_request: GetChatHistoryRequest,
    message_repository: Annotated[MessageRepository, Depends(get_message_repository)],
    notebook_repository: Annotated[NotebookRepository, Depends(get_notebook_repository)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[dict[str, str]]:
    return await llm_service.get_chat_history(
        chat_history_request, current_user, message_repository, notebook_repository
    )
