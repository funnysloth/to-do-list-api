# Imports from external libraries
from sqlmodel import Field, SQLModel, Relationship


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
                                                cascade_delete=True,
                                                sa_relationship_kwargs={"lazy": "selectin"})
    
class UserPublic(SQLModel):
    id: int
    username: str

