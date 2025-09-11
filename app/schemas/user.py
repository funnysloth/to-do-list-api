# Imports from external libraries
from fastapi import Form

# Imports from app modules
from app.models.user import *

class UserCredentials(SQLModel):
    username: str = Form()
    password: str = Form()

class UserUpdate(SQLModel):
    username: str | None = Form(default=None)
    password: str | None = Form(default=None)
    message: str
