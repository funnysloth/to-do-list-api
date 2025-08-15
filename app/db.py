# Imports from external libraries
from sqlmodel import SQLModel, create_engine, text
from sqlalchemy.engine import Engine

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
    return create_engine(DB_URL, echo=True, connect_args=connect_args)

def create_db_and_tables(engine: Engine):
    '''
    Creates the database and all tables defined in the models.
    '''
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))

def main():
    engine = create_db_engine()
    create_db_and_tables(engine)


if __name__ == "__main__":
    main()