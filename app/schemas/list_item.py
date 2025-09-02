# Imports from external libraries
from pydantic import BaseModel

# IMports from app modules
from app.models.list_item import *

class ListItemResponseBase(BaseModel):
    message: str

class ListItemsCreatedResponse(ListItemResponseBase):
    list_items: list['ListItemPublic']

class ListItemsRetrievedResponse(ListItemResponseBase):
    list_items: list['ListItemPublic'] | None

class ListItemRetrievedResponse(ListItemResponseBase):
    list_item: ListItemPublic

class ListItemUpdateResponse(ListItemResponseBase):
    list_item: ListItemPublic

class ListItemDeletedResponse(ListItemResponseBase):
    pass