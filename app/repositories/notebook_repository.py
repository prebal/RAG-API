from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notebook_model import Notebook


class NotebookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_notebooks_by_user(self, user_id: int) -> list[Notebook]:
        query = select(Notebook).where(Notebook.notebook_owner_id == user_id)

        return (await self.db.execute(query)).scalars().all()

    async def get_notebook_by_id(
        self, notebook_id: int, user_id: int
    ) -> Notebook | None:
        query = select(Notebook).where(
            Notebook.id == notebook_id, Notebook.notebook_owner_id == user_id
        )
        db_results = await self.db.scalar(query)

        return db_results

    async def get_notebook_by_name(
        self, notebook_name: str, user_id: int
    ) -> Notebook | None:
        query = select(Notebook).where(
            Notebook.notebook_name == notebook_name,
            Notebook.notebook_owner_id == user_id,
        )

        return await self.db.scalar(query)

    async def delete_notebook(self, notebook_id: int, user_id: int) -> None:
        notebook_to_delete = await self.get_notebook_by_id(notebook_id, user_id)

        if notebook_to_delete is None:
            raise HTTPException(
                400,
                detail="This notebook doesn't exist or you don't have the authorization to access it",
            )

        await self.db.delete(notebook_to_delete)
        await self.db.commit()

    async def modify_timestamp(self, notebook_id: int, user_id: int) -> None:
        notebook_to_modify = await self.get_notebook_by_id(notebook_id, user_id)

        if notebook_to_modify is None:
            raise HTTPException(
                400,
                detail="This notebook doesn't exist or you don't have the authorization to access it",
            )

        notebook_to_modify.last_accessed_at = datetime.now(UTC)

        await self.db.commit()

    async def create_notebook(self, new_notebook: Notebook) -> None:
        self.db.add(new_notebook)
        await self.db.commit()
        await self.db.refresh(new_notebook)
