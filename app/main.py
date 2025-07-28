from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import create_db_engine, create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables(db_engine)
    yield


app = FastAPI(lifespan=lifespan)
db_engine = create_db_engine()


@app.get("/")
def root():
    return {
        "Hello": "world"
    }