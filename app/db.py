# Imports from external libraries
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

# Imports from app modules
from app.models import *
from app.config import settings

def create_db_engine():
    '''
    Creates a database engine using the provided DB_URL.
    '''
    return create_async_engine(settings.DB_URL, echo=False)

async def create_db_and_tables(engine: AsyncEngine):
    '''
    Creates the database and all tables defined in the models.
    '''
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

async def get_session():
    '''
    handles session dependency.
    Yields a session, that way one session per request restraint is guaranteed
    '''
    async with AsyncSession(db_engine) as session:
        yield session

db_engine = create_db_engine()