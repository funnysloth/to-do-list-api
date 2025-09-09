# Imports from external libraries
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession


# Imports from app modules
from app.models.list import List, ListCreate, ListUpdate
from app.models.user import User
from app.crud.list_item_crud import craete_multiple_list_items
from app.exceptions import ListNotFoundException

# Imports from standard library
from datetime import datetime


async def get_list_by_id(session: AsyncSession, id: int) -> List | None:
    """Get a list by its ID."""
    result = await session.execute(select(List).where(List.id == id))
    return result.scalars().first()

async def get_user_lists(session: AsyncSession, user_id: int, sort_by: str | None = None, sort_order: str | None = None) -> list[List]:
    """Get all lists of a user."""
    if sort_by and sort_order:
        lists = await session.execute(select(List).where(List.user_id == user_id).order_by(sort_by, sort_order))
    elif sort_by:
        lists = await session.execute(select(List).where(List.user_id == user_id).order_by(sort_by))
    else:
        lists = await session.execute(select(List).where(List.user_id == user_id))
    return list(lists.scalars().all())

async def get_user_lists_by_name(session: AsyncSession, name: str, user_id: int, sort_by: str | None = None, sort_order: str | None = None) -> list[List]:
    """Get all lists of a user by name."""
    if sort_by and sort_order:
        lists = await session.execute(select(List).where(List.user_id == user_id, List.name.ilike(f"%{name}%")).order_by(sort_by, sort_order)) #type: ignore
    elif sort_by:
        lists = await session.execute(select(List).where(List.user_id == user_id, List.name.ilike(f"%{name}%")).order_by(sort_by))#type: ignore
    else:
        lists = await session.execute(select(List).where(List.user_id == user_id, List.name.ilike(f"%{name}%")))#type: ignore
    return list(lists.scalars().all())
    

async def create_list(session: AsyncSession, list: ListCreate, user_id: int) -> List:
    """Create a new list."""
    list_dict = list.model_dump()
    list_dict["user_id"] = user_id
    db_list = List.model_validate(list_dict)
    db_list.last_modified_at = db_list.created_at
    session.add(db_list)
    await session.commit()
    await session.refresh(db_list)
    if list.list_items:
        await craete_multiple_list_items(session, list.list_items, db_list) #type:ignore
    await session.refresh(db_list)
    return db_list

async def update_list(session: AsyncSession, list: List, list_updates:ListUpdate) -> List:
    """Update a list."""
    new_list_data = list_updates.model_dump(exclude_unset=True)
    list.sqlmodel_update(new_list_data)
    list.last_modified_at = datetime.now()
    session.add(list)
    await session.commit()
    await session.refresh(list)
    return list

async def delete_list(session: AsyncSession, list_id: int, user: User) -> None:
    """Delete a list."""
    list = get_user_list_by_id(user, list_id)
    if list is None:
        raise ListNotFoundException()
    await session.delete(list)
    await session.commit()

def get_user_list_by_id(user: User, list_id: int) -> List | None:
    """
    Searches for a list by its id within the user lists
    Get a specific list by its ID for a given user.
    """
    if user.lists is None:
        return None
    for list in user.lists:
        if list.id == list_id:
            return list
    else:
        return None