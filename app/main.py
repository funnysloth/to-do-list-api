# Imports from external libraries
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

# Imports from app modules
from app.db import create_db_engine, create_db_and_tables
from app.routes import user, list, list_item
from app.logging_config import setup_logging

# Imports from standard library
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Executes some startup and shutdown logic.
    Startup logic is before "yield" keyword.
    Shutodnw logic is after the 'yield" keyword
    '''
    setup_logging()
    logger.info("Starting up...")
    await create_db_and_tables(db_engine)
    yield
    logger.info("Shutting down...")

# Initialize app, db and essentials
app = FastAPI(
    lifespan=lifespan,
    title="To-Do List API",
    description="""
API for managing to‑do lists and list items.

This API supports JWT authentication and provides endpoints for creating, retrieving,
updating, and deleting lists and list items. Interactive documentation is available
via Swagger UI (/docs) and ReDoc (/redoc).
""",
    version="1.0.0"
)
db_engine = create_db_engine()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for request {Request.method} {request.url}", exc_info=True)
    return JSONResponse(status_code=500, content={"message": "Internal server error"})

# <---------- ROUTES ---------->

@app.get("/")
async def get_root():
    """
    Returns a simple welcome message and API status.
    """
    return {
        "message": "Welcome to the To-Do List API!",
        "status": "ok",
        "documentation": "/docs"
    }

app.include_router(user.router)
app.include_router(list.router)
app.include_router(list_item.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)