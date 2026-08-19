from fastapi import APIRouter, Depends

from app.database import get_db
from app.dependencies import get_current_user
from app.services.llm_service import LLMService
from app.schemas.llm_schema import LLMRequest

llm_router = APIRouter(prefix="/llm")

llm_service = LLMService("local", "llama3.2:1b")


@llm_router.post("/ask_question")
def ask_question(
    llm_request: LLMRequest, current_user=Depends(get_current_user), db=Depends(get_db)
):
    return llm_service.response(llm_request, current_user, db)
