from sqlmodel import Field, SQLModel
from datetime import datetime

class List(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    created_at: datetime
    last_modified_at: datetime
    is_deleted: bool
    user_id: int = Field(foreign_key="user.id")