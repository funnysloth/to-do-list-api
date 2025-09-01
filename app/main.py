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
import app.crud.user_crud as user_crud
import app.crud.list_crud as list_crud
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
        print("TOKEN ================> ", token)
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

@app.post("/register", response_model=UserPublic)
def create_user(user: UserCredentials, session: Session = Depends(get_session)):
    db_user = User.model_validate(user)
    if user_crud.get_user_by_username(session, db_user.username):
        raise HTTPException(status_code=400, detail="User with the same username already exists. Please choose another username.")
    created_user = user_crud.create_user(session, db_user)
    return created_user

@app.post("/login")
def login(user: UserCredentials, session: Session = Depends(get_session)):
    try:
        authenticated_user = user_crud.authenticacte_user(session, user)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail = e)
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=400, detail=e)
    else:
        access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
        access_token = create_access_token(UserPublic.model_validate(authenticated_user), access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    
@app.patch("/users", response_model=UserPublic)
def update_user(
    user: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="You are not authenticated.")
    updated_user = user_crud.update_user(session, current_user, user)
    return updated_user

@app.delete("/users")
def delete_user(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user_crud.delete_user(session, current_user)
    return {"message": "User deleted successfully"}

@app.post("/lists", response_model=ListPublic)
def create_list(
    list: ListCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    new_list = list_crud.create_list(session, list, current_user.id)
    return new_list

@app.get("/lists", response_model=list[ListPublic])
def get_lists(
    current_user: User = Depends(get_current_user)
):
    print("USER ====================> ", current_user)
    print("REQUEST --------------------------------------")
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    return current_user.lists

app.get("/lists/{list_id}", response_model=ListPublic)
def get_list_by_Id(
        list_id: int,
        current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unathorized.")
    found_list = list_crud.get_user_list_by_id(current_user, list_id)
    if not found_list:
        raise HTTPException(status_code=404, detail="The list with such an id wasn't found within user lists.")
    return found_list