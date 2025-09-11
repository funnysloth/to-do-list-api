# Imports from app modules
from app.models.list import *
from app.schemas.list_item import ListItemUpdate


class ListCreate(SQLModel):
    name: str
    list_items: list[str] | None = None

class ListUpdate(SQLModel):
    name: str | None = None
    list_items: list['ListItemUpdate'] | None = None