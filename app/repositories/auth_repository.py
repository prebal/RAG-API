from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth_model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def request_user_by_email(
        self,
        email_to_check: str,
    ) -> User | None:

        db_query = select(User).where(User.email == email_to_check)
        return self.db.scalar(db_query)

    def request_user_by_name(
        self,
        name_to_check: str,
    ) -> User | None:

        db_query = select(User).where(User.username == name_to_check)
        return self.db.scalar(db_query)

    def request_user_by_id(
        self,
        id_to_check: str | int,
    ) -> User | None:

        db_query = select(User).where(User.id == id_to_check)
        return self.db.scalar(db_query)

    def create_user(
        self,
        new_user: User,
    ) -> None:

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

    def change_username(
        self,
        current_user: User,
        new_username: str,
    ) -> User | None:

        current_user.username = new_username
        self.db.commit()

        return current_user

    def change_password(
        self,
        current_user: User,
        new_password_hash: str,
    ) -> User | None:
        current_user.password_hash = new_password_hash
        self.db.commit()

        return current_user
