# Imports from external libraries
from pydantic import BaseModel

# Imports from app modules
from app.models.list import *

class ListResponseBase(BaseModel):
    message: str

class ListCreateResponse(ListResponseBase):
    list: ListPublic

class ListsRetrieveResponse(ListResponseBase):
    lists: list['ListPublic'] | None

class SingleListRetrieveResponse(ListResponseBase):
    list: ListPublic

class ListUpdateResponse(ListResponseBase):
    list: ListPublic

class ListDeleteResponse(ListResponseBase):
    pass