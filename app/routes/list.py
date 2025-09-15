# Imports from external libraries
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Imports from app modules
from app.schemas.list import *
from app.schemas.base import *
import app.crud.list_crud as list_crud
import app.crud.list_item_crud as list_items_crud
from app.models.user import User
from app.db import get_session
from app.utils import *

# Imports from standard library
import math

router = APIRouter(prefix="/lists", tags=["Lists"])


@router.post("", response_model=ResponseBase)
async def create_list(
    list: ListCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    new_list = await list_crud.create_list(session, list, current_user.id)
    if list.list_items:
        await list_items_crud.create_list_items(session, list.list_items, new_list)
        await session.refresh(new_list)
    return ResponseBase(message="List created successfully", data={
        "list": ListPublic.model_validate(new_list)
    })


@router.get("", response_model=ResponseBase)
async def get_lists(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    name : str | None = None,
    sort_by: SortBy | None = None,
    sort_order: SortOrder | None = None,
    page: int = 1,
    page_size: int = 10
):        
    lists, total_items = await list_crud.get_user_lists(session, current_user.id, name, sort_by, sort_order, page, page_size)
    if len(lists) == 0:
        return ResponseBase(message="No lists were found with such parameters.", data={
            "lists": []
        })
    lists_public = [ListPublic.model_validate(list) for list in lists]
    return ResponseBase(message="Lists retrieved successfully", data={
        "lists": lists_public,
        "total_items": total_items,
        "total_pages": math.ceil(total_items / page_size) if page_size > 0 else 0,
        "page": page,
        "page_size": page_size
    })


@router.get("/{list_id}", response_model=ResponseBase)
async def get_list_by_Id(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The list with such an id wasn't found within user lists.")
    return ResponseBase(message="List retrieved successfully", data={
        "list": ListPublic.model_validate(found_list)
    })

@router.patch("/{list_id}", response_model=ResponseBase)
async def update_list(
    list_id: int,
    list: ListUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The list with such an id wasn't found within user lists.")
    updated_list = await list_crud.update_list(session, found_list, list)
    return ResponseBase(message="List updated successully", data={
        "list": ListPublic.model_validate(updated_list)
    })


@router.delete("/{list_id}", response_model=ResponseBase)
async def delete_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The list with such an id wasn't found within user lists.")
    await list_crud.delete_list(session, found_list)
    return ResponseBase(message="List deleted successfully", data=None)