from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import Engine
from app.models import *
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL") or ""
if not DB_URL:
    raise ValueError("DB_URL environment varibale is not set.")

def create_db_engine():
    return create_engine(DB_URL, echo=True)

def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)

def main():
    engine = create_db_engine()
    create_db_and_tables(engine)


if __name__ == "__main__":
    main()