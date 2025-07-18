from sqlmodel import Field, SQLModel, Relationship
from app.models.list import List

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str

    lists: list['List'] | None = Relationship(back_populates="user", 
                                                cascade_delete=True, 
                                                passive_deletes="all")