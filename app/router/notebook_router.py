from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_notebook_service
from app.models.auth_model import User
from app.models.notebook_model import Notebook
from app.schemas.notebook_schema import NotebookRequest, NotebookResponse
from app.services.notebook_service import NotebookService

notebook_router = APIRouter(prefix="/notebooks")


@notebook_router.post("/create_notebook")
async def create_notebook(
    request: NotebookRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    notebook_service: Annotated[NotebookService, Depends(get_notebook_service)],
) -> dict[str, str]:

    await notebook_service.create_new_notebook(request, current_user)

    return {"message": "A new notebook has been successfully created"}


@notebook_router.delete("/delete_notebook")
async def delete_notebook(
    request: NotebookRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    notebook_service: Annotated[NotebookService, Depends(get_notebook_service)],
) -> dict[str, str]:
    await notebook_service.delete_notebook(request, current_user)

    return {"message": "The notebook has been deleted"}


@notebook_router.get("/get_all_notebooks", response_model=list[NotebookResponse])
async def get_all_notebooks(
    current_user: Annotated[User, Depends(get_current_user)],
    notebook_service: Annotated[NotebookService, Depends(get_notebook_service)],
) -> list[Notebook]:
    return await notebook_service.get_all_notebooks(current_user)
