# Imports from external libraries
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

# Imports from app modules
from app.models.user import User, UserCredentials, UserUpdate
from app.exceptions import UserNotFoundException, InvalidCredentialsException

pwd_context =  CryptContext(schemes=["sha256_crypt"])


async def get_user_by_username(session: AsyncSession, username: str) -> User | None :
    '''
    Selects a user from the database by their username.
    '''
    result = await session.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None :
    '''
    Selects a user from the database by their id.
    '''
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

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

async def create_user(session: AsyncSession, user: User) -> User:
    '''
    Creates a new user in the database.
    '''
    extra_data = {"password": get_password_hash(user.password)}
    user.sqlmodel_update(extra_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def authenticate_user(session: AsyncSession, user: UserCredentials) -> User:
    '''
    Authenticates a user by their username and password.
    '''
    found_user = await get_user_by_username(session, user.username)
    if not found_user:
        raise UserNotFoundException("Invalid username.")
    if not verify_password(user.password, found_user.password):
        raise InvalidCredentialsException("Invalid password.")
    return found_user


async def update_user(session: AsyncSession, user: User, updated_data: UserUpdate) -> User:
    '''
    Updates a user in the database.
    '''
    if updated_data.password:
        updated_data.password = get_password_hash(updated_data.password)
    new_user_data = updated_data.model_dump(exclude_unset=True)
    user.sqlmodel_update(new_user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def delete_user(session: AsyncSession, user: User) -> None:
    '''
    Deletes a user from the database.
    '''
    await session.delete(user)
    await session.commit()