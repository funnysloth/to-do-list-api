from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from app.models.list import List

class ListItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default=datetime.now())
    last_modified_at: datetime = Field(default=datetime.now())
    is_completed: bool = Field(default=False)
    list_id: int = Field(foreign_key="list.id", ondelete="CASCADE")

    list: List = Relationship(back_populates="list_items")
