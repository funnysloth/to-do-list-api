from app.models.user import User
from sqlmodel import select, Session


def get_user_by_username(session: Session, username: str) -> User | None :
    return session.exec(select(User).where(User.username == username)).first()


def create_user(session: Session, user: User):
    
    session.add(user)
    session.commit() 
