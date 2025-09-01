from sqlmodel import SQLModel
from datetime import datetime

class ListItemCreate(SQLModel):
    content: str

class ListItemUpdate(SQLModel):
    content: str | None = None
    is_completed: bool | None = None

class ListItemPublic(SQLModel):
    id: int
    content: str
    created_at: datetime
    last_modified_at: datetime
    is_completed: bool