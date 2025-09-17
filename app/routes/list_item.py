# Imports from external libraries
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession

# Imports from app modules
from app.schemas.list_item import *
from app.schemas.base import *
import app.crud.list_crud as list_crud
import app.crud.list_item_crud as list_item_crud
from app.models.user import User
from app.db import get_session
from app.utils import get_current_user

# Imports from standard library
import math

router = APIRouter(prefix="/lists/{list_id}/items", tags=["List Items"])


@router.post("", 
             summary="Create list items",
             description="""
Creates one or more list items in the specified list.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Parameters**: 
  - *list_id* [path]: The ID of the list.
  - *list_items* [body]: An array of strings representing the content for each list item.
  
Returns the created list items.
""",
             response_model=ResponseWithData[ListItems])
async def create_list_item(
    list_id: int,
    list_items: list[str] = Body(
        ...,
        description="An array of list item contents to be created.",
        example=["Buy milk", "Walk the dog", "Call mom"]
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No list with such an id was found within user lists")
    created_items = await list_item_crud.create_list_items(session, list_items, found_list)
    public_items = [ListItemPublic.model_validate(item) for item in created_items]
    return ResponseWithData(message="List items created successfully", data={"list_items": public_items})


@router.get("", 
            summary="Retrieve list items",
            description="""
Retrieves list items for the specified list with pagination support.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Parameters**:
  - *list_id* [path]: The ID of the list.
  - *page* [query]: The page number to retrieve (default is 1).
  - *page_size* [query]: The number of items per page (default is 10).

Returns the list items along with pagination details.
""",
            response_model=ResponseWithPagination[ListsItemsPagination])
async def get_list_items(
    list_id: int,
    page: int = Query(1, ge=1, description="The page number to retrieve."),
    page_size: int = Query(10, ge=1, description="Number of items per page."),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No list with such an id was found within user lists")
    list_items, total_items = await list_item_crud.get_list_items(session, list_id, current_user.id, page, page_size)
    message = "List items retrieved successfully" if list_items else "No list items were found within the specified list."
    list_items_public = [ListItemPublic.model_validate(item) for item in list_items or []]
    return ResponseWithPagination(message=message, data={
        "list_items": list_items_public,
        "total_items": total_items,
        "total_pages": math.ceil(total_items / page_size) if page_size > 0 else 0,
        "page": page,
        "page_size": page_size
    })


@router.get("/{list_item_id}", 
            summary="Retrieve a specific list item",
            description="""
Retrieves the details of a specific list item by its ID within the specified list.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Parameters**:
  - *list_id* [path]: The ID of the list.
  - *list_item_id* [path]: The ID of the list item to retrieve.

Returns the specified list item.
""",
            response_model=ResponseWithData[SpecificListItem])
async def get_list_item(
    list_id: int,
    list_item_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    list_item = await list_item_crud.get_list_item_by_id(session, list_item_id, list_id, current_user.id)
    if not list_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find the specified list item.")
    return ResponseWithData(message="List item retrieved successfully", data={"list_item": ListItemPublic.model_validate(list_item)})


@router.patch("/{list_item_id}", 
              summary="Update a list item",
              description="""
Updates a specific list item identified by its ID within the specified list.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Parameters**:
  - *list_id* [path]: The ID of the list.
  - *list_item_id* [path]: The ID of the list item.
  - *list_item* [body]: The fields to update (supports partial updates).
  
Returns the updated list item.
""",
              response_model=ResponseWithData[SpecificListItem])
async def update_list_item(
    list_id: int,
    list_item_id: int,
    list_item: ListItemUpdate = Body(
        ...,
        description="The updated fields for the list item.",
        example={
            "content": "Buy bread and eggs",
            "completed": True
        }
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list_item = await list_item_crud.get_list_item_by_id(session, list_item_id, list_id, current_user.id)
    if found_list_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find the specified list item in the specified list.")
    updated_list_item = await list_item_crud.update_list_item(session, found_list_item, found_list_item.list, list_item)
    return ResponseWithData(message="List item updated successfully", data={"list_item": ListItemPublic.model_validate(updated_list_item)})


@router.delete("/{list_item_id}", 
               summary="Delete a list item",
               description="""
Deletes a specific list item identified by its ID within the specified list.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Parameters**:
  - *list_id* [path]: The ID of the list.
  - *list_item_id* [path]: The ID of the list item to delete.
  
Returns a success message upon deletion.
""",
               response_model=ResponseWithNoData)
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
    return ResponseWithNoData(message="List item deleted successfully")