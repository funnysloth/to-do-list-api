from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from jwt.exceptions import InvalidTokenError

# Imports from app modules
import app.crud.user_crud as user_crud
from app.models.user import User, UserPublic
from app.db import get_session
from app.config import settings

# Imports from standard library
from datetime import datetime, timedelta, timezone
from typing import Any

def create_token(data: dict[str, Any], expires_delta: timedelta, token_type: str, secret: str) -> str:
    '''
    Creates and returns JWT token
    '''
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "type": token_type
    })
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=settings.JWT_ALGORITHM) # type: ignore
    return encoded_jwt

def generate_access_and_refresh_tokens(user: User) -> tuple[str, str]:
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    user_public = UserPublic.model_validate(user)
    access_token = create_token(user_public.model_dump(), access_token_expires, "access_token", settings.JWT_SECRET) #type:ignore
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
    refresh_token_data = {
        "user_id": user_public.id
    }
    refresh_token = create_token(refresh_token_data, refresh_token_expires, "refresh_token", settings.REFRESH_TOKEN_SECRET) #type:ignore
    return ( access_token, refresh_token)

async def get_current_user(access_token: str = Header(), session: AsyncSession = Depends(get_session)) -> User:
    '''
    Decodes the JWT access token and retrieves user from the DB.
    '''
    creds_ecxeption = HTTPException(status_code=401,
                                    detail="invaliid or expired access token.")
    if not access_token:
        raise HTTPException(status_code=401, detail="You are not authenticated.")
    try:
        payload = jwt.decode(access_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]) #type: ignore
        username = payload.get("username")
        if username is None:
            raise creds_ecxeption
        found_user = await user_crud.get_user_by_username(session, username)
    except InvalidTokenError:
        raise creds_ecxeption
    if not found_user:
        raise creds_ecxeption
    return found_user

async def validate_refresh_token(refresh_token: str = Header(), session: AsyncSession = Depends(get_session)) -> User:
    '''
    Decodes the JWT refresh token and retrieves user from the DB.
    '''
    creds_ecxeption = HTTPException(status_code=401,
                                    detail="invaliid or expired refresh token.")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="You are not authenticated.")
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=[settings.JWT_ALGORITHM]) #type: ignore
        user_id = payload.get("user_id")
        if user_id is None:
            raise creds_ecxeption
        found_user = await user_crud.get_user_by_id(session, user_id)
    except InvalidTokenError:
        raise creds_ecxeption
    if not found_user:
        raise creds_ecxeption
    return found_user