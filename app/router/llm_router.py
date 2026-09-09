from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_current_user, get_llm_service
from app.models.auth_model import User
from app.schemas.llm_schema import LLMRequest
from app.services.llm_service import LLMService

llm_router = APIRouter(prefix="/llm")


@llm_router.post("/ask_question")
async def ask_question(
    llm_request: LLMRequest,
    llm_service: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    return StreamingResponse(
        llm_service.response(llm_request, current_user),
        media_type="text/event-stream",
    )
