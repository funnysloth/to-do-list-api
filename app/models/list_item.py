# IMports from external libraries
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING


if TYPE_CHECKING:
# Imports from app modules
    from app.models.list import List

# Imports from standard library
from datetime import datetime

class ListItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    content: str
    last_modified_at: datetime = Field(default_factory=datetime.now)
    is_completed: bool = Field(default=False)
    list_id: int = Field(foreign_key="list.id", ondelete="CASCADE")

    list: 'List' = Relationship(back_populates="list_items")

class ListItemUpdate(SQLModel):
    content: str | None = None
    is_completed: bool | None = None

class ListItemPublic(SQLModel):
    id: int
    content: str
    created_at: datetime
    last_modified_at: datetime
    is_completed: bool
