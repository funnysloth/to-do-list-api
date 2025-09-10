# Imports from external libraries
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Imports from app modules
from app.schemas.list import *
import app.crud.list_crud as list_crud
from app.models.user import User
from app.main import get_session
from app.utils import *

router = APIRouter(prefix="/lists", tags=["lists"])


@router.post("", response_model=ListCreateResponse)
async def create_list(
    list: ListCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    new_list = await list_crud.create_list(session, list, current_user.id)
    return ListCreateResponse(message="List created successfully", list=ListPublic.model_validate(new_list))


@router.get("", response_model=ListsRetrieveResponse)
async def get_lists(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    name : str | None = None,
    sort_by: SortBy | None = None,
    sort_order: SortOrder | None = None
):        
    lists = await list_crud.get_user_lists(session, current_user.id, name, sort_by, sort_order)
    if len(lists) == 0:
        return ListsRetrieveResponse(message="There are no lists.", lists=[])
    lists_public = [ListPublic.model_validate(lst) for lst in lists or []]
    return ListsRetrieveResponse(message="Lists retrieved successfully", lists=lists_public)


@router.get("/{list_id}", response_model=SingleListRetrieveResponse)
async def get_list_by_Id(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=404, detail="The list with such an id wasn't found within user lists.")
    return SingleListRetrieveResponse(message="List retrieved successfully", list=ListPublic.model_validate(found_list))


@router.delete("/{list_id}", response_model=ListDeleteResponse)
async def delete_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=404, detail="The list with such an id wasn't found within user lists.")
    await list_crud.delete_list(session, found_list)
    return ListDeleteResponse(message="List deleted successfully")