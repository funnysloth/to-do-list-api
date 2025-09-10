# Imports from external libraries
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from jwt.exceptions import InvalidTokenError

# Imports from app modules
from app.db import create_db_engine, create_db_and_tables
from app.schemas.user import *
from app.schemas.list import *
from app.schemas.list_item import *
import app.crud.user_crud as user_crud
import app.crud.list_crud as list_crud
import app.crud.list_item_crud as list_item_crud
from app.models.user import User
from app.exceptions import *

# Imports from standard library
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import re
from typing import Any

# load environment variables
load_dotenv()

# CONSTANTS
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "7"))
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^\w\s])\S{8,}$')

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Executes some startup and shutdown logic.
    Startup logic is before "yield" keyword.
    Shutodnw logic is after the 'yield" keyword
    '''
    await create_db_and_tables(db_engine)
    yield

# Initialize app, db and essentials
app = FastAPI(lifespan=lifespan)
db_engine = create_db_engine()
oath2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_session():
    '''
    handles session dependency.
    Yields a session, that way one session per request restraint is guaranteed
    '''
    async with AsyncSession(db_engine) as session:
        yield session


# <---------- AUTH HELPER FUNCTIONS ---------->

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


# <---------- USER RELATED ROUTES ---------->

@app.post("/register", response_model=UserCreateRespoonse)
async def create_user(user: UserCredentials, session: AsyncSession = Depends(get_session)):
    db_user = User.model_validate(user)
    if await user_crud.get_user_by_username(session, db_user.username):
        raise HTTPException(status_code=400, detail="User with the same username already exists. Please choose another username.")
    if not PASSWORD_REGEX.match(db_user.password):
        raise HTTPException(status_code=404, detail="The password you provided is weak. It should contain at least 1 lowercase letter, 1 uppercase letter, 1 digit and 1 speecial character")
    created_user = user_crud.create_user(session, db_user)
    return UserCreateRespoonse(message="User created successfully", user=UserPublic.model_validate(created_user))


@app.post("/login", response_model=UserLoginResponse)
async def login(response: Response, user: UserCredentials, session: AsyncSession = Depends(get_session)):
    try:
        authenticated_user = await user_crud.authenticacte_user(session, user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    else:
        access_token, refresh_token, access_token_expire_datetime, refresh_token_expire_datetime = generate_access_and_refresh_tokens(authenticated_user)
        response.set_cookie(key="access_token", value=access_token, secure=True, httponly=True, expires=access_token_expire_datetime)
        response.set_cookie(key="refresh_token", value=refresh_token, secure=True, httponly=True, expires=refresh_token_expire_datetime)
        return UserLoginResponse(message="Login successful")


@app.patch("/users", response_model=UserUpdateResponse)
async def update_user(
    user: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user.username and await user_crud.get_user_by_username(session, user.username):
        raise HTTPException(status_code=400, detail="The user with such a username already exists.")
    if user.password and not PASSWORD_REGEX.match(user.password):
        raise HTTPException(status_code=404, detail="The password you provided is weak. It should contain at least 1 lowercase letter, 1 uppercase letter, 1 digit and 1 speecial character")
    updated_user = user_crud.update_user(session, current_user, user)
    return UserUpdateResponse(message="user updated successfully", user=UserPublic.model_validate(updated_user))


@app.delete("/users", response_model=UserDeleteResponse)
async def delete_user(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    await user_crud.delete_user(session, current_user)
    return UserDeleteResponse(message="User deleted successfully")


# <--------- LIST RELATED ROUTES ---------->

@app.post("/lists", response_model=ListCreateResponse)
async def create_list(
    list: ListCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    new_list = await list_crud.create_list(session, list, current_user.id)
    return ListCreateResponse(message="List created successfully", list=ListPublic.model_validate(new_list))


@app.get("/lists", response_model=ListsRetrieveResponse)
async def get_lists(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    name : str | None = None,
    sort_by: SortBy | None = None,
    sort_order: SortOrder | None = None
):        
    lists = await list_crud.get_user_lists(session, current_user.id, name, sort_by, sort_order)
    if len(lists) == 0:
        return ListsRetrieveResponse(message="There are no lists.", lists=[])
    lists_public = [ListPublic.model_validate(lst) for lst in lists or []]
    return ListsRetrieveResponse(message="Lists retrieved successfully", lists=lists_public)


@app.get("/lists/{list_id}", response_model=SingleListRetrieveResponse)
async def get_list_by_Id(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=404, detail="The list with such an id wasn't found within user lists.")
    return SingleListRetrieveResponse(message="List retrieved successfully", list=ListPublic.model_validate(found_list))


@app.delete("/lists/{list_id}", response_model=ListDeleteResponse)
async def delete_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=404, detail="The list with such an id wasn't found within user lists.")
    await list_crud.delete_list(session, found_list)
    return ListDeleteResponse(message="List deleted successfully")


@app.post("/lists/{list_id}/items", response_model=ListItemsCreatedResponse)
async def create_list_item(
    list_id: int,
    list_items: list[str],
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=404, detail="No list with such an id was found within user lists")
    created_items = await list_item_crud.craete_list_itemss(session, list_items, found_list)
    public_items = [ListItemPublic.model_validate(item) for item in created_items]
    return ListItemsCreatedResponse(message="List items created successfully", list_items=public_items)


# <--------- LIST ITEM RELATED ROUTES ---------->

@app.get("/lists/{list_id}/items", response_model=ListItemsRetrievedResponse)
async def get_list_items(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    list_items = await list_item_crud.get_list_items(session, list_id, current_user.id)
    list_items_public = [ListItemPublic.model_validate(item) for item in list_items or []]
    return ListItemsRetrievedResponse(message="List items retrieved successfully", list_items=list_items_public)


@app.get("/lists/{list_id}/items/{list_item_id}", response_model=ListItemRetrievedResponse)
async def get_list_item(
    list_id: int,
    list_item_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    list_item = await list_item_crud.get_list_item_by_id(session, list_item_id, list_id, current_user.id)
    if not list_item:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list item.")
    return ListItemRetrievedResponse(message="List item retrieved successfully", list_item=ListItemPublic.model_validate(list_item))


@app.patch("/lists/{list_id}/items/{list_item_id}", response_model=ListItemUpdateResponse)
async def update_list_item(
    list_id: int,
    list_item_id: int,
    list_item: ListItemUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list_item = await list_item_crud.get_list_item_by_id(session, list_item_id, list_id, current_user.id)
    if found_list_item is None:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list item in the specified list.")
    updated_liat_item = await list_item_crud.update_list_item(session, found_list_item, found_list_item.list, list_item)
    return ListItemUpdateResponse(message="List item updated successfully", list_item=ListItemPublic.model_validate(updated_liat_item))


@app.delete("/lists/{list_id}/items/{list_item_id}", response_model=ListItemDeletedResponse)
async def delete_list_item(
    list_id: int,
    list_item_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list_item = await list_item_crud.get_list_item_by_id(session, list_item_id, list_id, current_user.id)
    if found_list_item is None:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list item in the specified list.")
    await list_item_crud.delete_list_Item(session, found_list_item)
    return ListItemDeletedResponse(message="List item deleted successfully")