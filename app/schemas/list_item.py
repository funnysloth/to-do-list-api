# IMports from app modules
from app.models.list_item import *

class ListItemUpdate(SQLModel):
    content: str | None = None
    is_completed: bool | None = None
