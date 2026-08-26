from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token_model import RefreshToken


class TokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_token(self, refresh_token: RefreshToken) -> None:
        self.db.add(refresh_token)
        await self.db.commit()

    async def revoke_token(self, token_hash: str, user_id: int) -> None:
        recovered_token = await self.find_active_token_by_hash(token_hash, user_id)

        if recovered_token is not None:
            recovered_token.valid = False

        await self.db.commit()

    async def find_active_token_by_hash(
        self, token_hash: str, user_id: int
    ) -> RefreshToken | None:
        query = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.token_hash == token_hash,
            RefreshToken.valid.is_(True),
        )
        return await self.db.scalar(query)

    async def revoke_all_for_user(self, user_id: int) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.valid.is_(True))
            .values(valid=False)
        )
        await self.db.commit()
