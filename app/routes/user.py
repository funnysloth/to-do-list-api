# Imports from external libraries
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

# Imports from app modules
from app.schemas.user import *
from app.schemas.base import *
import app.crud.user_crud as user_crud
from app.models.user import User
from app.exceptions import UserNotFoundException, InvalidCredentialsException
from app.db import get_session
from app.utils import get_current_user, generate_access_and_refresh_tokens, validate_refresh_token

# Imports from standard library
import re

# CONSTANTS
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^\w\s])\S{8,}$')

router = APIRouter(prefix="", tags=["Users"])


@router.post("/register",
             summary="Register a new user",
             description="""
Registers a new user by providing the required details.

- **Body Parameters**:
  - *username*: The desired username.
  - *password*: A strong password meeting complexity requirements.
  
Returns the newly created user.
""",
             response_model=ResponseWithData[UserInfo])
async def create_user(
    user: UserCredentials = Body(..., example={
        "username": "john_doe",
        "password": "StrongPassword123!"
    }),
    session: AsyncSession = Depends(get_session)
):
    db_user = User.model_validate(user)
    if await user_crud.get_user_by_username(session, db_user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the same username already exists. Please choose another username."
        )
    if not PASSWORD_REGEX.match(db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password you provided is weak. It should contain at least 1 lowercase letter, 1 uppercase letter, 1 digit and 1 special character."
        )
    created_user = await user_crud.create_user(session, db_user)
    return ResponseWithData(message="User created successfully", data={
        "user": UserPublic.model_validate(created_user)
    })


@router.post("/login",
             summary="User login",
             description="""
Authenticates a user using the provided credentials.

- **Body Parameters**:
  - *username*: The username of the user.
  - *password*: The user's password.
  
On successful authentication, returns a JWT access token and a refresh token.
""",
             response_model=ResponseWithData[AccessToken])
async def login(
    user: UserCredentials = Body(..., example={
        "username": "john_doe",
        "password": "StrongPassword123!"
    }),
    session: AsyncSession = Depends(get_session)
):
    try:
        authenticated_user = await user_crud.authenticate_user(session, user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    access_token, refresh_token = generate_access_and_refresh_tokens(authenticated_user.id)
    return ResponseWithData(message="Login successful", data={
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token
    })


@router.get("/me",
            summary="Retrieve own profile",
            description="""
Retrieves the profile details of the currently authenticated user.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
  
Returns the user's profile information.
""",
            response_model=ResponseWithData[UserInfo])
def get_me(current_user: User = Depends(get_current_user)):
    return ResponseWithData(message="User retrieved successfully", data={
        "user": UserPublic.model_validate(current_user)
    })


@router.patch("/users",
              summary="Update user data",
              description="""
Modifies details of the currently authenticated user.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Body Parameters**:
  - *username* (optional): The new username.
  - *password* (optional): The new password which must meet the complexity requirements.
  
Returns the updated user data.
""",
              response_model=ResponseWithData[UserInfo])
async def update_user(
    user: UserUpdate = Body(..., example={
        "username": "john_doe_updated",
        "password": "AnotherStrongPassword123!"
    }),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user.username and await user_crud.get_user_by_username(session, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with such a username already exists."
        )
    if user.password and not PASSWORD_REGEX.match(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password you provided is weak. It should contain at least 1 lowercase letter, 1 uppercase letter, 1 digit and 1 special character."
        )
    updated_user = await user_crud.update_user(session, current_user, user)
    return ResponseWithData(message="User updated successfully", data={
        "user": UserPublic.model_validate(updated_user)
    })


@router.delete("/users",
               summary="Delete a user",
               description="""
Deletes the currently authenticated user.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
  
Returns a success message upon deletion.
""",
               response_model=ResponseWithNoData)
async def delete_user(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    await user_crud.delete_user(session, current_user)
    return ResponseWithNoData(message="User deleted successfully")


@router.post("/refresh-token",
             summary="Refresh JWT access token",
             description="""
Generates new JWT access and refresh tokens using a valid refresh token.

- **Body Parameters**:
  - *refresh_token*: The refresh token issued previously.
  
Returns the new JWT access token and refresh token.
""",
             response_model=ResponseWithData[AccessToken])
def refresh_token(
    current_user: User = Depends(validate_refresh_token)
):
    access_token, new_refresh_token = generate_access_and_refresh_tokens(current_user.id)
    return ResponseWithData(message="Token refreshed successfully", data={
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": new_refresh_token
    })
