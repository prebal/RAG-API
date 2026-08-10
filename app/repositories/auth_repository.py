
from app.models.auth_model import User
from sqlalchemy import select
from sqlalchemy.orm import Session


class UserRepository:
    def request_user_by_email(self, 
                              email_to_check: str, 
                              db: Session
                              ) -> User | None:

        db_query = select(User).where(User.email == email_to_check)
        return db.scalar(db_query)
        
    def request_user_by_name(self, 
                             name_to_check: str, 
                             db: Session
                             ) -> User | None:

        db_query = select(User).where(User.username == name_to_check)
        return db.scalar(db_query)

    def request_user_by_id(self, 
                           id_to_check: str | int, 
                           db: Session
                           ) -> User | None:

        db_query = select(User).where(User.id == id_to_check)
        return db.scalar(db_query)

    def create_user(self, 
                    new_user: User, 
                    db: Session
                    ) -> None:

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    def change_username(self, 
                        current_user: User, 
                        new_username: str, 
                        db: Session
                        ) -> User | None:

        current_user.username = new_username
        db.commit()

        return current_user

    def change_password(self, 
                        current_user: User, 
                        new_password_hash: str, 
                        db: Session
                        ) -> User | None:
        current_user.password_hash = new_password_hash
        db.commit()

        return current_user
