# Imports from external libraries
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, asc

# Imports from app modules
from app.models.list_item import ListItem
from app.schemas.list_item import ListItemUpdate
from app.models.list import List

# Imports from standard library
from datetime import datetime


async def create_list_items(session: AsyncSession, list_items: list[str], to_do_list: List) -> list[ListItem]:
    """
    Creates list items in the list and stores them in the db
    """
    items : list['ListItem'] = []

    for item in list_items:
        list_item_dict = {}
        list_item_dict["content"] = item
        list_item_dict["list_id"] = to_do_list.id
        db_list_item = ListItem.model_validate(list_item_dict)
        session.add(db_list_item)
        items.append(db_list_item)
    
    to_do_list.last_modified_at = datetime.now()
    session.add(to_do_list)
    await session.commit()
    for item in items:
        await session.refresh(item)
    await session.refresh(to_do_list)
    
    return items


async def get_list_items(
        session: AsyncSession, 
        list_id: int, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
) -> tuple[list['ListItem'], int]:
    """
    Retrieve and return all list items within the user's list.
    """
    conditions = [ListItem.list_id == list_id, List.user_id == user_id]
    count_query = select(func.count(ListItem.id)).join(List).where(*conditions) #type: ignore
    total_items_result = await session.execute(count_query)
    total_items = total_items_result.scalar_one()
    if total_items == 0:
        return [], 0

    offset = (page - 1) * page_size
    list_items = await session.execute(select(ListItem).join(List).where(*conditions).order_by(asc(ListItem.created_at)).offset(offset).limit(page_size))
    return list(list_items.scalars().all()), total_items


async def get_list_item_by_id(session: AsyncSession, list_item_id: int, list_id: int, user_id: int) -> ListItem | None:
    """
    Search for a list item by its ID within the list and return it if found; otherwise, return None.
    """
    list_item = await session.execute(select(ListItem).join(List).where(ListItem.id == list_item_id,
                                                                         ListItem.list_id == list_id,
                                                                         List.user_id == user_id))
    return list_item.scalars().first()


async def update_list_item(
        session: AsyncSession,
        list_item: ListItem, 
        list: List, 
        updated_list_item: ListItemUpdate
) -> ListItem:
    """
    Updates the list item by its id within the list and save it in the database.
    """
    new_data = updated_list_item.model_dump(exclude_unset=True)
    list_item.sqlmodel_update(new_data)
    list_item.last_modified_at = datetime.now()
    list.last_modified_at = datetime.now()
    session.add(list_item)
    session.add(list)
    await session.commit()
    await session.refresh(list_item)
    await session.refresh(list)
    return list_item


async def delete_list_item(session: AsyncSession, list_item: ListItem) -> None:
    """
    Deletes the list item by its id within the list.
    """
    await session.delete(list_item)
    list_item.list.last_modified_at = datetime.now()
    await session.commit()