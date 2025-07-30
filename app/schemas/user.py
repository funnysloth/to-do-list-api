from sqlmodel import SQLModel

class UserCreate(SQLModel):
    username: str
    password: str

class UserPublic(SQLModel):
    id: int
    username: str

class UserUpdate(SQLModel):
    username: str | None
    password: str | None