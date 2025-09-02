# Imports from external libraries
from sqlmodel import Field, SQLModel, Relationship
from fastapi import Form


# Imports from standard library
from typing import TYPE_CHECKING

# Imports for type checking
if TYPE_CHECKING:
    from app.models.list import List


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str

    lists: list['List'] | None = Relationship(back_populates="user", 
                                                cascade_delete=True)
    
class UserCredentials(SQLModel):
    username: str = Form()
    password: str = Form()

class UserPublic(SQLModel):
    id: int
    username: str

class UserUpdate(SQLModel):
    username: str | None = Form(default=None)
    password: str | None = Form(default=None)