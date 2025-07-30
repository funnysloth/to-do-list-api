from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from .db import create_db_engine, create_db_and_tables
from .schemas.user import *
import app.crud.user_crud as user_crud
from .models.user import User
from sqlmodel import Session

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables(db_engine)
    yield

app = FastAPI(lifespan=lifespan)
db_engine = create_db_engine()

def get_session():
    with Session(db_engine) as session:
        yield session

@app.get("/")
def root():
    return {
        "Hello": "world"
    }

@app.post("/user", response_model=UserPublic)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.model_validate(user)
    created_user = user_crud.create_user(session, db_user)
    return created_user