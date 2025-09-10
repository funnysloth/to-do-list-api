from fastapi import Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from jwt.exceptions import InvalidTokenError

# Imports from app modules
import app.crud.user_crud as user_crud
from app.models.user import User, UserPublic
from app.main import get_session

# Imports from standard library
from datetime import datetime, timedelta, timezone
from typing import Any
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# CONSTANTS
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "7"))
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")

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
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=JWT_ALGORITHM) # type: ignore
    return encoded_jwt

def generate_access_and_refresh_tokens(user: User) -> tuple[str, str, datetime, datetime]:
    access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    user_public = UserPublic.model_validate(user)
    access_token = create_token(user_public.model_dump(), access_token_expires, "access_token", JWT_SECRET) #type:ignore
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)
    refresh_token_data = {
        "user_id": user_public.id
    }
    refresh_token = create_token(refresh_token_data, refresh_token_expires, "refresh_token", REFRESH_TOKEN_SECRET) #type:ignore
    access_token_expire_datetime = datetime.now(timezone.utc) + access_token_expires
    refresh_token_expire_datetime = datetime.now(timezone.utc) + refresh_token_expires
    return ( access_token, refresh_token, access_token_expire_datetime, refresh_token_expire_datetime)

async def get_current_user(request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> User:
    '''
    Decodes the JWT access token and retrieves user from the DB.
    '''
    creds_ecxeption = HTTPException(status_code=401,
                                    detail="invaliid or expired access token.")
    access_token = request.cookies.get("access_token", "")
    if not access_token:
        raise HTTPException(status_code=401, detail="You are not authenticated.")
    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM]) #type: ignore
        username = payload.get("username")
        if username is None:
            raise creds_ecxeption
        found_user = await user_crud.get_user_by_username(session, username)
    except InvalidTokenError:
        refresh_token = request.cookies.get("refresh_token", "")
        if not refresh_token:
            raise creds_ecxeption
        try:
            payload = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET, algorithms=[JWT_ALGORITHM]) #type: ignore
            user_id = payload.get("user_id")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid refresh token.")
            
            found_user = await user_crud.get_user_by_id(session, user_id)
            if not found_user:
                raise HTTPException(status_code=401, detail="Invalid refresh token.")
   
            access_token, refresh_token, access_token_expire_datetime, refresh_token_expire_datetime = generate_access_and_refresh_tokens(found_user)
            response.set_cookie(key="access_token", value=access_token, secure=True, httponly=True, expires=access_token_expire_datetime)
            response.set_cookie(key="refresh_token", value=refresh_token, secure=True, httponly=True, expires=refresh_token_expire_datetime)
        
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token.")
    if not found_user:
        raise creds_ecxeption
    return found_user