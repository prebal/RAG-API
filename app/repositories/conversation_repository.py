from fastapi import HTTPException
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation_model import Conversation

class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_conversation_entry(self, conversation_id: int, user_id: int) -> Conversation:
        query = select(Conversation).where(Conversation.id = conversation_id, Conversation.conversation_owner = user_id)
        db_results = await self.db.scalar(query)

        if db_results is None:
            raise HTTPException(400, detail = "This conversation doesn't exist or you don't have the authorization to access it")

        return db_results

    async def delete_conversation(self, conversation_id: int, user_id: int):
        conversation_to_delete = await self.get_conversation_entry(conversation_id, user_id)

        await self.db.delete(conversation_to_delete)
        await self.db.commit()

    async def modify_timestamp(self, conversation_id: int, user_id: int):
        conversation_to_modify = await self.get_conversation_entry(conversation_id, user_id)
        conversation_to_modify.last_accessed_at = datetime.now(UTC)

        await self.db.commit()

    async def create_conversation(self, new_conversation):
        self.db.add(new_conversation)
        await self.db.commit()
        await self.db.refresh(new_conversation)
