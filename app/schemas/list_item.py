# Imports from external libraries
from pydantic import BaseModel

# IMports from app modules
from app.models.list_item import *

class ListItemUpdate(SQLModel):
    content: str | None = None
    is_completed: bool | None = None

class ListsItemsPagination(BaseModel):
    list_items: list[ListItemPublic]
    total_items: int
    total_pages: int
    page: int
    page_size: int

class ListItems(BaseModel):
    list_items: list[ListItemPublic]

class SpecificListItem(BaseModel):
    list_item: ListItemPublic