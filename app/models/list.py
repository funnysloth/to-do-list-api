# Imports from external libraries
from sqlmodel import Field, SQLModel, Relationship

# Imports from standard library
from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

from app.models.list_item import ListItem, ListItemPublic

# Imports for type checking
if TYPE_CHECKING:
    from app.models.user import User

class List(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_modified_at: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    user: 'User' = Relationship(back_populates="lists")
    list_items: list['ListItem'] | None = Relationship(back_populates="list", 
                                                       cascade_delete=True, 
                                                       sa_relationship_kwargs={"lazy": "selectin"})

class ListPublic(SQLModel):
    id: int
    name: str
    list_items: list['ListItemPublic'] | None = None
    created_at: datetime
    last_modified_at: datetime

class SortBy(str, Enum):
    sort_name = "name"
    created_at = "created_at"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
