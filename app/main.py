# Imports from external libraries
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
from sqlmodel import Session
import jwt
from jwt.exceptions import InvalidTokenError

# Imports from app modules
from app.db import create_db_engine, create_db_and_tables
from app.schemas.user import *
from app.schemas.list import *
from app.schemas.list_item import *
from app.models.list_item import ListItemCreate
import app.crud.user_crud as user_crud
import app.crud.list_crud as list_crud
import app.crud.list_item_crud as list_item_crud
from app.models.user import User
from app.exceptions import UserNotFoundException, InvalidCredentialsException

# Imports from standard library
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# load environment variables
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Executes some startup and shutdown logic.
    Startup logic is before "yield" keyword.
    Shutodnw logic is after the 'yield" keyword
    '''
    create_db_and_tables(db_engine)
    yield

#Initialize app, db and essentials
app = FastAPI(lifespan=lifespan)
db_engine = create_db_engine()
oath2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_session():
    '''
    handles session dependency.
    Yields a session, that way one session per request restraint is guaranteed
    '''
    with Session(db_engine) as session:
        yield session


def create_access_token(user: UserPublic, expires_delta: timedelta | None = None) -> str:
    '''
    Creates and returns JWT access token
    '''
    to_encode = user.model_dump().copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM) # type: ignore
    return encoded_jwt


def get_current_user(token: str = Header(), session: Session = Depends(get_session)) -> User:
    '''
    Decodes the JWT access token and retrieves user from the DB.
    '''
    creds_ecxeption = HTTPException(status_code=401,
                                    detail="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]) #type: ignore
        username = payload.get("username")
        if username is None:
            raise creds_ecxeption
    except InvalidTokenError:
        raise creds_ecxeption
    user = user_crud.get_user_by_username(session, username)
    if not user:
        raise creds_ecxeption
    return user


@app.post("/register", response_model=UserCreateRespoonse)
def create_user(user: UserCredentials, session: Session = Depends(get_session)):
    db_user = User.model_validate(user)
    if user_crud.get_user_by_username(session, db_user.username):
        raise HTTPException(status_code=400, detail="User with the same username already exists. Please choose another username.")
    created_user = user_crud.create_user(session, db_user)
    return UserCreateRespoonse(message="User created successfully", user=UserPublic.model_validate(created_user))


@app.post("/login", response_model=UserLoginResponse)
def login(user: UserCredentials, session: Session = Depends(get_session)):
    try:
        authenticated_user = user_crud.authenticacte_user(session, user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    else:
        access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
        access_token = create_access_token(UserPublic.model_validate(authenticated_user), access_token_expires)
        return UserLoginResponse(message="Login successful", access_token=access_token, token_type="Bearer")


@app.patch("/users", response_model=UserUpdateResponse)
def update_user(
    user: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="You are not authenticated.")
    if user.username and user_crud.get_user_by_username(session, user.username):
        raise HTTPException(status_code=400, detail="The user with such a username already exists.")
    updated_user = user_crud.update_user(session, current_user, user)
    return UserUpdateResponse(message="user updated successfully", user=UserPublic.model_validate(updated_user))


@app.delete("/users", response_model=UserDeleteResponse)
def delete_user(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user_crud.delete_user(session, current_user)
    return UserDeleteResponse(message="User deleted successfully")


@app.post("/lists", response_model=ListCreateResponse)
def create_list(
    list: ListCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    new_list = list_crud.create_list(session, list, current_user.id)
    return ListCreateResponse(message="List created successfully", list=ListPublic.model_validate(new_list))


@app.get("/lists", response_model=ListsRetrieveResponse)
def get_lists(
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    if current_user.lists is None:
        return ListsRetrieveResponse(message="You haven't created any list yet", lists=[])
    if len(current_user.lists) == 0:
        return ListsRetrieveResponse(message="You haven't created any list yet", lists=[])
    lists_public = [ListPublic.model_validate(lst) for lst in current_user.lists or []]
    return ListsRetrieveResponse(message="Lists retrieved successfully", lists=lists_public)


@app.get("/lists/{list_id}", response_model=SingleListRetrieveResponse)
def get_list_by_Id(
        list_id: int,
        current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    found_list = list_crud.get_user_list_by_id(current_user, list_id)
    if not found_list:
        raise HTTPException(status_code=404, detail="The list with such an id wasn't found within user lists.")
    return SingleListRetrieveResponse(message="List retrieved successfully", list=ListPublic.model_validate(found_list))


@app.delete("/lists/{list_id}", response_model=ListDeleteResponse)
def deelte_list(
    list_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    list_crud.delete_list(session, list_id, current_user)
    return ListDeleteResponse(message="List deleted successfully")


@app.post("/lists/{list_id}/items", response_model=ListItemsCreatedResponse)
def create_list_item(
    list_id: int,
    list_items: list[ListItemCreate],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    if not list_crud.get_user_list_by_id(current_user, list_id):
        raise HTTPException(status_code=403, detail="Unathorized")
    created_items: list['ListItemPublic'] = []
    for item in list_items:
        new_item = list_item_crud.create_list_item(session, item, list_id)
        created_items.append(ListItemPublic.model_validate(new_item))

    return ListItemsCreatedResponse(message="List items created successfully", list_items=created_items)


@app.get("/lists/{list_id}/items", response_model=ListItemsRetrievedResponse)
def get_list_items(
    list_id: int,
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    list = list_crud.get_user_list_by_id(current_user, list_id)
    if not list:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list.")
    if list.list_items is None:
        return ListItemsRetrievedResponse(message="There are no items in this list.", list_items=[])
    if len(list.list_items) == 0:
        return ListItemsRetrievedResponse(message="There are no items in this list.", list_items=[])
    list_items_public = [ListItemPublic.model_validate(item) for item in list.list_items or []]
    return ListItemsRetrievedResponse(message="List items retrieved successfully", list_items=list_items_public)


@app.get("/lists/{list_id}/items/{list_item_id}", response_model=ListItemRetrievedResponse)
def get_list_item(
    list_id: int,
    list_item_id: int,
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    list = list_crud.get_user_list_by_id(current_user, list_id)
    if not list:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list.")
    list_item = list_item_crud.get_list_item_by_id(list_item_id, list)
    if not list_item:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list item.")
    return ListItemRetrievedResponse(message="List item retrieved successfully", list_item=ListItemPublic.model_validate(list_item))


@app.patch("/lists/{list_id}/items/{list_item_id}", response_model=ListItemUpdateResponse)
def update_list_item(
    list_id: int,
    list_item_id: int,
    list_item: ListItemUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    list = list_crud.get_user_list_by_id(current_user, list_id)
    if not list:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list.")
    list_item_crud.update_list_item(session, list_item_id, list, list_item)
    return ListItemUpdateResponse(message="List item updated successfully", list_item=ListItemPublic.model_validate(list_item))


@app.delete("/lists/{list_id}/items/{list_item_id}", response_model=ListItemDeletedResponse)
def delete_list_item(
    list_id: int,
    list_item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    list = list_crud.get_user_list_by_id(current_user, list_id)
    if not list:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list.")
    list_item_crud.delete_list_Item(session, list_item_id, list)
    return ListItemDeletedResponse(message="List item deleted successfully")