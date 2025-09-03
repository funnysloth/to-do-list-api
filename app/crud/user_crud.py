# Imports from external libraries
from sqlmodel import select, Session
from passlib.context import CryptContext

# Imports from app modules
from app.models.user import User, UserCredentials, UserUpdate
from app.exceptions import UserNotFoundException, InvalidCredentialsException

pwd_context =  CryptContext(schemes=["sha256_crypt"])


def get_user_by_username(session: Session, username: str) -> User | None :
    '''
    Selects a user from the database by their username.
    '''
    return session.exec(select(User).where(User.username == username)).first()

def get_password_hash(password: str) -> str:
    '''
    Hashes a password using the SHA-256 algorithm.
    '''
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    '''
    Verifies a password against a hashed password.
    '''
    return pwd_context.verify(plain_password, hashed_password)

def create_user(session: Session, user: User) -> User:
    '''
    Creates a new user in the database.
    '''
    extra_data = {"password": get_password_hash(user.password)}
    user.sqlmodel_update(extra_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def authenticacte_user(session: Session, user: UserCredentials) -> User | None:
    '''
    Authenticates a user by their username and password.
    '''
    found_user = get_user_by_username(session, user.username)
    if not found_user:
        raise UserNotFoundException("Invalid username.")
    if not verify_password(user.password, found_user.password):
        raise InvalidCredentialsException("Invalid password.")
    return found_user


def update_user(session: Session, user: User, updated_data: UserUpdate) -> User:
    '''
    Updates a user in the database.
    '''
    if updated_data.password:
        updated_data.password = get_password_hash(updated_data.password)
    new_user_data = updated_data.model_dump(exclude_unset=True)
    user.sqlmodel_update(new_user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def delete_user(session: Session, user: User) -> None:
    '''
    Deletes a user from the database.
    '''
    session.delete(user)
    session.commit()