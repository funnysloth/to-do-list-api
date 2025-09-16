# Imports from external libraries
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Imports from app modules
from app.schemas.user import *
from app.schemas.base import *
import app.crud.user_crud as user_crud
from app.models.user import User
from app.exceptions import *
from app.db import get_session
from app.utils import *

# Imports from standard library
import re

# CONSTANTS
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^\w\s])\S{8,}$')

router = APIRouter(prefix="", tags=["Users"])

@router.post("/register",
             summary="Register a new user", 
             description="""
Register a new user.\n
Expects *username* and *password* as form urlencoded parameters.\n
Returns the created user.
             """,
             response_model=ResponseBase)
async def create_user(user: UserCredentials, session: AsyncSession = Depends(get_session)):
    db_user = User.model_validate(user)
    if await user_crud.get_user_by_username(session, db_user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with the same username already exists. Please choose another username.")
    if not PASSWORD_REGEX.match(db_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The password you provided is weak. It should contain at least 1 lowercase letter, 1 uppercase letter, 1 digit and 1 speecial character")
    created_user = await user_crud.create_user(session, db_user)
    return ResponseBase(message="User created successfully", data={
        "user": UserPublic.model_validate(created_user)
    })


@router.post("/login", 
             summary="Login a user",
             description="""
Logins a user.\n
Expects *username* and *password* as form urlencoded parameters.\n
Returns the JWT access token and refresh token.
""",
             response_model=ResponseBase)
async def login(user: UserCredentials, session: AsyncSession = Depends(get_session)):
    try:
        authenticated_user = await user_crud.authenticate_user(session, user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        access_token, refresh_token = generate_access_and_refresh_tokens(authenticated_user.id)
        return ResponseBase(message="Login successful", data={
            "access_token": access_token,
            "token_type": "Bearer",
            "refresh_token": refresh_token
        })

@router.patch("/users", 
                summary="Modifies user data.",
                description="""
Modifies user data..\n
Requires authorization with JWT token in *Authorization* header.\n
Expects optional *username* and *password* as form urlencoded parameters.\n
Returns the updated user.
""",
                response_model=ResponseBase)
async def update_user(
    user: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user.username and await user_crud.get_user_by_username(session, user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user with such a username already exists.")
    if user.password and not PASSWORD_REGEX.match(user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The password you provided is weak. It should contain at least 1 lowercase letter, 1 uppercase letter, 1 digit and 1 speecial character")
    updated_user = await user_crud.update_user(session, current_user, user)
    return ResponseBase(message="user updated successfully", data={
        "user": UserPublic.model_validate(updated_user)
    })


@router.delete("/users",
                summary="Deletes a user",
                description="""
Deletes a user.\n
Requires authorization with JWT token in *Authorization* header.\n
""",
                response_model=ResponseBase)
async def delete_user(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    await user_crud.delete_user(session, current_user)
    return ResponseBase(message="User deleted successfully", data=None)


@router.post("/refresh-token",
             summary="Refreshes JWT acess token",
             description="""
Refreshes JWT acess token.\n
Expects *refresh_token* body parameter.\n
Returns the new JWT access token and refresh token.
""",
              response_model=ResponseBase)
def refresh_token(current_user: User = Depends(validate_refresh_token)):
    access_token, refresh_token = generate_access_and_refresh_tokens(current_user.id)
    return ResponseBase(message="Login successful", data={
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token
    })
    