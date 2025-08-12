from app.models.user import User
from app.schemas.user import UserCredentials
from sqlmodel import select, Session
from passlib.context import CryptContext
from app.exceptions import UserNotFoundException, InvalidCredentialsException

pwd_context =  CryptContext(schemes=["sha256_crypt"])


def get_user_by_username(session: Session, username: str) -> User | None :
    return session.exec(select(User).where(User.username == username)).first()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(session: Session, user: User) -> User:
    extra_data = {"password": get_password_hash(user.password)}
    user.sqlmodel_update(extra_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def authenticacte_user(session: Session, user: UserCredentials) -> User | None:
    found_user = get_user_by_username(session, user.username)
    if not found_user:
        raise UserNotFoundException("Invalid username.")
    if not verify_password(found_user.password, user.password):
        raise InvalidCredentialsException("Invalid password.")
    return found_user