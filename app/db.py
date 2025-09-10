# Imports from external libraries
from sqlmodel import SQLModel, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

# Imports from app modules
from app.models import *

# Imports from standard library
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

DB_URL = os.getenv("DB_URL") or ""
if not DB_URL:
    raise ValueError("DB_URL environment varibale is not set.")

def create_db_engine():
    '''
    Creates a database engine using the provided DB_URL.
    '''
    connect_args = {"check_same_thread": False}
    return create_async_engine(DB_URL, echo=True, connect_args=connect_args)


async def create_db_and_tables(engine: AsyncEngine):
    '''
    Creates the database and all tables defined in the models.
    '''
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
        await connection.execute(text("PRAGMA foreign_keys=ON"))

async def get_session():
    '''
    handles session dependency.
    Yields a session, that way one session per request restraint is guaranteed
    '''
    async with AsyncSession(db_engine) as session:
        yield session



db_engine = create_db_engine()