from sqlalchemy.orm import Session
from sqlalchemy import select
from models.auth_models import User
from typing import Union

class UserRepository():
    def request_user_by_email(self, email_to_check: str, db: Session) -> Union[User, None]:
        db_query = select(User).where(User.email == email_to_check)
        return db.scalar(db_query)
        
    def request_user_by_name(self, name_to_check: str, db: Session) -> Union[User, None]:
        db_query = select(User).where(User.login_name == name_to_check)
        return db.scalar(db_query)

    def create_user(self, new_user: User, db: Session) -> None:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

