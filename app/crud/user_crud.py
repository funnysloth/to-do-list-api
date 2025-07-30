from app.models.user import User
from sqlmodel import select, Session
from passlib.hash import pbkdf2_sha256


def get_user_by_username(session: Session, username: str) -> User | None :
    return session.exec(select(User).where(User.username == username)).first()


def create_user(session: Session, user: User) -> User:
    extra_data = {"password": pbkdf2_sha256.hash(user.password)}
    user.sqlmodel_update(extra_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user