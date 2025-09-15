from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

# Imports from app modules
from app.schemas.list_item import *
from app.schemas.base import *
import app.crud.list_crud as list_crud
import app.crud.list_item_crud as list_item_crud
from app.models.user import User
from app.db import get_session
from app.utils import *

# Imports from standard library
import math

router = APIRouter(prefix="/lists/{list_id}/items", tags=["List items"])

@router.post("", response_model=ResponseBase)
async def create_list_item(
    list_id: int,
    list_items: list[str] = Body(),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No list with such an id was found within user lists")
    created_items = await list_item_crud.create_list_items(session, list_items, found_list)
    public_items = [ListItemPublic.model_validate(item) for item in created_items]
    return ResponseBase(message="List items created successfully", data={
        "list_items": public_items
    })

@router.get("", response_model=ResponseBase)
async def get_list_items(
    list_id: int,
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No list with such an id was found within user lists")
    list_items, total_items = await list_item_crud.get_list_items(session, list_id, current_user.id, page, page_size)
    message = "List items retrieved successfully"
    if len(list_items) == 0:
        message = "No list items were found within the specified list."
        
    list_items_public = [ListItemPublic.model_validate(item) for item in list_items or []]
    return ResponseBase(message=message, data={
        "list_items": list_items_public,
        "total_items": total_items,
        "total_pages": math.ceil(total_items / page_size) if page_size > 0 else 0,
        "page": page,
        "page_size": page_size
    })

@router.get("/{list_item_id}", response_model=ResponseBase)
async def get_list_item(
    list_id: int,
    list_item_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    list_item = await list_item_crud.get_list_item_by_id(session, list_item_id, list_id, current_user.id)
    if not list_item:
        raise HTTPException(status_code=404, detail="Couldn't find the specified list item.")
    return ResponseBase(message="List item retrieved successfully", data={
        "list_item": ListItemPublic.model_validate(list_item)
    })

@router.patch("/{list_item_id}", response_model=ResponseBase)
async def update_list_item(
    list_id: int,
    list_item_id: int,
    list_item: ListItemUpdate = Body(),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list_item = await list_item_crud.get_list_item_by_id(session, list_item_id, list_id, current_user.id)
    if found_list_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find the specified list item in the specified list.")
    updated_liat_item = await list_item_crud.update_list_item(session, found_list_item, found_list_item.list, list_item)
    return ResponseBase(message="List item updated successfully", data={
        "list_item": ListItemPublic.model_validate(updated_liat_item)
    })


@router.delete("/{list_item_id}", response_model=ResponseBase)
async def delete_list_item(
    list_id: int,
    list_item_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list_item = await list_item_crud.get_list_item_by_id(session, list_item_id, list_id, current_user.id)
    if found_list_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find the specified list item in the specified list.")
    await list_item_crud.delete_list_item(session, found_list_item)
    
    return ResponseBase(message="List item deleted successfully", data=None)