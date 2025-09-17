# Imports from external libraries
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

# Imports from app modules
from app.schemas.list import *
from app.schemas.base import *
import app.crud.list_crud as list_crud
import app.crud.list_item_crud as list_items_crud
from app.models.user import User
from app.db import get_session
from app.utils import get_current_user

# Imports fomr standard library
import math

router = APIRouter(prefix="/lists", tags=["Lists"])

@router.post("", 
             summary="Create a new to-do list",
             description="""
Creates a new to-do list for the authenticated user.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Body Parameters**:
  - *name*: The title of the to-do list.
  - *list_items* [optional]: An array of strings representing the content for each list item.
  
If the request includes list items, they will be added to the newly created list.
""",
             response_model=ResponseWithData[SpecificList])
async def create_list(
    list: ListCreate = Body(
        ...,
        description="The details for the new list.",
        example={
            "name": "My Daily Tasks",
            "list_items": ["Buy groceries", "Read a book"]
        }
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    new_list = await list_crud.create_list(session, list, current_user.id)
    if list.list_items:
        await list_items_crud.create_list_items(session, list.list_items, new_list)
        await session.refresh(new_list)
    return ResponseWithData(message="List created successfully", data={
        "list": ListPublic.model_validate(new_list)
    })

@router.get("", 
            summary="Retrieve user lists",
            description="""
Retrieves all to-do lists belonging to the authenticated user with optional filtering and sorting.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Query Parameters**:
  - *name* [optional]: Filter lists by name.
  - *sort_by* [optional]: Field to sort by. Avaialbel options: name, created_at.
  - *sort_order* [optional]: The order of sorting. Available options: asc or desc.
  - *page*: The page number to retrieve (default is 1).
  - *page_size*: The number of lists per page (default is 10).

Returns a paginated list of to-do lists.
""",
            response_model=ResponseWithPagination[ListsPagination])
async def get_lists(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    name: str | None = Query(None, description="Optional filter by list name."),
    sort_by: SortBy | None = Query(None, description="Field to sort by: name or created_at."),
    sort_order: SortOrder | None = Query(None, description="Sort order: asc or desc."),
    page: int = Query(1, ge=1, description="The page number to retrieve."),
    page_size: int = Query(10, ge=1, description="The number of lists per page.")
):        
    lists, total_items = await list_crud.get_user_lists(session, current_user.id, name, sort_by, sort_order, page, page_size)
    message = "Lists retrieved successfully" if len(lists) > 0 else "No lists were found with such parameters."
    
    lists_public = [ListPublic.model_validate(lst) for lst in lists]

    return ResponseWithPagination(message=message, data={
        "lists": lists_public,
        "total_items": total_items,
        "total_pages": math.ceil(total_items / page_size) if page_size > 0 else 0,
        "page": page,
        "page_size": page_size
    })

@router.get("/{list_id}", 
            summary="Retrieve a specific to-do list",
            description="""
Retrieves the details of a specific to-do list identified by its ID.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Path Parameter**:
  - *list_id*: The ID of the to-do list.

Returns the to-do list details.
""",
            response_model=ResponseWithData[SpecificList])
async def get_list_by_Id(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The list with such an id wasn't found within user lists.")
    return ResponseWithData(message="List retrieved successfully", data={
        "list": ListPublic.model_validate(found_list)
    })

@router.patch("/{list_id}", 
              summary="Update a to-do list",
              description="""
Updates information for a specific to-do list.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Path Parameter**:
  - *list_id*: The ID of the to-do list.
- **Body Parameters**:
  - *name*: The title of the to-do list.

Returns the updated to-do list.
""",
              response_model=ResponseWithData[SpecificList])
async def update_list(
    list_id: int,
    list: ListUpdate = Body(
        ...,
        description="The fields to update for the list.",
        example={
            "name": "Updated name"
        }
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The list with such an id wasn't found within user lists.")
    updated_list = await list_crud.update_list(session, found_list, list)
    return ResponseWithData(message="List updated successfully", data={
        "list": ListPublic.model_validate(updated_list)
    })

@router.delete("/{list_id}", 
               summary="Delete a to-do list",
               description="""
Deletes the to-do list specified by its ID.

- **Authorization**: Requires a valid JWT token in the *Authorization* header.
- **Path Parameter**:
    - *list_id*: The ID of the to-do list to delete.

Returns a success message upon deletion.
""",
               response_model=ResponseWithNoData)
async def delete_list(
    list_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    found_list = await list_crud.get_user_list_by_id(session, current_user.id, list_id)
    if not found_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The list with such an id wasn't found within user lists.")
    await list_crud.delete_list(session, found_list)
    return ResponseWithNoData(message="List deleted successfully")