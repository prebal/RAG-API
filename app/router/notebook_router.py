from app.models.auth_model import User
from app.schemas.notebook_schema import NotebookRequest
from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.notebook_model import Notebook

notebook_router = APIRouter(prefix="/notebooks")


@notebook_routere.post("create_new_notebook")
async def create_new_notebook(
    request: NotebookRequest,
    current_user: User = Depends(get_current_user),
    notebook_service: NotebookService = Depends(get_notebook_service),
) -> dict[str, str]:

    await self.notebook_service.create_new_notebook(request, current_user)

    return {"message": "A new notebook has been successfully created"}
