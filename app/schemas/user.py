# Imports from external libraries
from pydantic import BaseModel

# Imports from app modules
from app.models.user import *

class UserResponseBase(BaseModel):
    message: str

class UserCreateRespoonse(UserResponseBase):
    user: UserPublic

class UserLoginResponse(UserResponseBase):
    message: str

class UserUpdateResponse(UserResponseBase):
    message: str
    user: UserPublic

class UserDeleteResponse(UserResponseBase):
    pass