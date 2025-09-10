# Imports from external libraries
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager

# Imports from app modules
from app.db import create_db_engine, create_db_and_tables
from app.routes import user, list, list_item


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


# <---------- ROUTES ---------->

app.include_router(user.router)
app.include_router(list.router)
app.include_router(list_item.router)