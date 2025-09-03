# Imports from external libraries
from sqlmodel import Field, SQLModel, Relationship

# Imports from standard library
from datetime import datetime
from typing import TYPE_CHECKING

from app.models.list_item import ListItem, ListItemUpdate
# Imports for type checking
if TYPE_CHECKING:
    from app.models.user import User

class List(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default=datetime.now())
    last_modified_at: datetime = Field(default=datetime.now())
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    user: 'User' = Relationship(back_populates="lists")
    list_items: list['ListItem'] | None = Relationship(back_populates="list", 
                                                       cascade_delete=True)
    
class ListCreate(SQLModel):
    name: str
    list_items: list[str] | None = None

class ListUpdate(SQLModel):
    name: str | None = None
    list_items: list['ListItemUpdate'] | None = None

class ListPublic(SQLModel):
    id: int
    name: str
    list_items: list['ListItem'] | None = None
    created_at: datetime
    last_modified_at: datetime