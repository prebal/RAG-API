from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_model import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def request_user_by_email(
        self,
        email_to_check: str,
    ) -> User | None:

        db_query = select(User).where(User.email == email_to_check)
        return await self.db.scalar(db_query)

    async def request_user_by_name(
        self,
        name_to_check: str,
    ) -> User | None:

        db_query = select(User).where(User.username == name_to_check)
        return await self.db.scalar(db_query)

    async def request_user_by_id(
        self,
        id_to_check: str | int,
    ) -> User | None:

        db_query = select(User).where(User.id == id_to_check)
        return await self.db.scalar(db_query)

    async def create_user(
        self,
        new_user: User,
    ) -> None:

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

    async def change_username(
        self,
        current_user: User,
        new_username: str,
    ) -> User | None:

        current_user.username = new_username
        await self.db.commit()

        return current_user

    async def change_password(
        self,
        current_user: User,
        new_password_hash: str,
    ) -> User | None:
        current_user.password_hash = new_password_hash
        await self.db.commit()

        return current_user

    async def delete_user(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
