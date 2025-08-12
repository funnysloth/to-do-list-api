from sqlmodel import SQLModel
from fastapi import Form

class UserCredentials(SQLModel):
    username: str = Form()
    password: str = Form()

class UserPublic(SQLModel):
    id: int
    username: str

class UserUpdate(SQLModel):
    username: str | None
    password: str | None