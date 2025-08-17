from sqlmodel import SQLModel
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.list_item import ListItem

class ListCreate(SQLModel):
    name: str
    items: list['ListItem'] | None = None

class ListUpdate(SQLModel):
    name: str | None = None
    items: list['ListItem'] | None = None

class ListPublic(SQLModel):
    id: int
    name: str
    items: list['ListItem']
    created_at: datetime