from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from app.models.list import List

class ListItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    created_at: datetime
    last_modified_at: datetime
    is_completed: bool
    is_deleted: bool
    list_id: int = Field(foreign_key="list.id", ondelete="CASCADE")

    list: List = Relationship(back_populates="list_items")
