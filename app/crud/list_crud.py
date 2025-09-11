# Imports from external libraries
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc

# Imports from app modules
from app.models.list import List
from app.schemas.list import ListCreate, ListUpdate

# Imports from standard library
from datetime import datetime

async def create_list(session: AsyncSession, list: ListCreate, user_id: int) -> List:
    """Create a new list."""
    list_dict = list.model_dump()
    list_dict["user_id"] = user_id
    db_list = List.model_validate(list_dict)
    db_list.last_modified_at = db_list.created_at
    session.add(db_list)
    await session.commit()
    await session.refresh(db_list)
    return db_list

async def get_user_lists(
        session: AsyncSession, 
        user_id: int, 
        name: str | None = None, 
        sort_by: str | None = None, 
        sort_order: str | None = None
) -> list[List]:
    """Get lists of a user."""
    conditions = [List.user_id == user_id]
    if name:
        conditions.append(List.name.ilike(f'%{name}%')) #type: ignore

    query = select(List).where(*conditions)
    if sort_by:
        col = getattr(List, sort_by, None)
        if col:
            if sort_order and sort_order == "desc":
                query = query.order_by(desc(col))
            else:
                query = query.order_by(asc(col))

    lists = await session.execute(query)
    return list(lists.scalars().all())
    
async def get_user_list_by_id(session: AsyncSession, user_id: int, list_id: int) -> List | None:
    """Searches for a list by its id and user's id."""
    found_list = await session.execute(select(List).where(List.id == list_id, List.user_id == user_id))
    return found_list.scalars().first()

async def update_list(session: AsyncSession, list: List, list_updates: ListUpdate) -> List:
    """Update a list."""
    new_list_data = list_updates.model_dump(exclude_unset=True)
    list.sqlmodel_update(new_list_data)
    list.last_modified_at = datetime.now()
    session.add(list)
    await session.commit()
    await session.refresh(list)
    return list

async def delete_list(session: AsyncSession, list: List) -> None:
    """Delete a list."""
    await session.delete(list)
    await session.commit()