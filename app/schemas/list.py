# Imports from app modules
from app.models.list import *


class ListCreate(SQLModel):
    name: str
    list_items: list[str] | None = None

class ListUpdate(SQLModel):
    name: str