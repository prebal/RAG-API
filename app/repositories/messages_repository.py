from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message_model import Message


class MessageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_message_by_id(self, message_id: int, user_id: int) -> Message:
        query = select(Message).where(
            Message.id == message_id, Message.message_owner_id == user_id
        )
        db_results = await self.db.scalar(query)

        if db_results is None:
            raise HTTPException(400, detail="A message couldn't be found")

        return db_results

    async def get_all_messages_by_notebook_id(
        self, notebook_id: int, user_id: int, message_limit: int = 10
    ):
        # DESC + limit grabs the LATEST N messages; reversed back so the
        # result stays in chronological order for prompt assembly.
        query = (
            select(Message.content, Message.role)
            .where(
                Message.notebook_assigned_id == notebook_id,
                Message.message_owner_id == user_id,
            )
            .order_by(Message.id.desc())
            .limit(message_limit)
        )

        rows = (await self.db.execute(query)).all()
        return rows[::-1]

    async def delete_message(self, message_id: int, user_id: int) -> None:
        message_to_delete = await self.get_message_by_id(message_id, user_id)

        await self.db.delete(message_to_delete)
        await self.db.commit()

    async def create_message(self, new_message: Message) -> None:
        self.db.add(new_message)
        await self.db.commit()
        await self.db.refresh(new_message)