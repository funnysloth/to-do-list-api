# Imports from external libraries
from pydantic import BaseModel

# Imports from app modules
from app.models.list import *
from app.schemas.base import *

class ListCreate(SQLModel):
    name: str
    list_items: list[str] | None = None

class ListUpdate(SQLModel):
    name: str

class ListsPagination(BaseModel):
    lists: list[ListPublic]
    total_items: int
    total_pages: int
    page: int
    page_size: int

class Lists(BaseModel):
    lists: list[ListPublic]

class SpecificList(BaseModel):
    list: ListPublic
