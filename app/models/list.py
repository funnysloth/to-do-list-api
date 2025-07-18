from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from app.models.user import User
from app.models.list_item import ListItem

class List(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    created_at: datetime
    last_modified_at: datetime
    is_deleted: bool
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    user: User = Relationship(back_populates="lists")
    list_items: list['ListItem'] | None = Relationship(back_populates="list", 
                                                       cascade_delete=True, 
                                                       passive_deletes=True)