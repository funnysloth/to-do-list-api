# Imports from external libraries
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
from sqlmodel import Session
import jwt

# Imports from app modules
from app.db import create_db_engine, create_db_and_tables
from app.schemas.user import *
import app.crud.user_crud as user_crud
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

#Initialize app and db
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
    to_encode = user.model_dump().copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM) # type: ignore
    return encoded_jwt

@app.get("/")
def root():
    return {
        "Hello": "world"
    }

@app.post("/register", response_model=UserPublic)
def create_user(user: UserCredentials, session: Session = Depends(get_session)):
    db_user = User.model_validate(user)
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