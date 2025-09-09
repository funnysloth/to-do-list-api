# Imports from external libraries
from sqlalchemy.ext.asyncio import AsyncSession


# Imports from app modules
from app.models.list_item import ListItem, ListItemUpdate
from app.models.list import List
from app.exceptions import ListItemNotFoundException

# Imports from standard library
from datetime import datetime


async def create_list_item(session: AsyncSession, list_item: str, list_id: int) -> ListItem:
    """
    Creates a new list item in the list and stores it in the db
    """
    list_item_dict = {}
    list_item_dict["content"] = list_item
    list_item_dict["list_id"] = list_id
    db_list_item = ListItem.model_validate(list_item_dict)
    session.add(db_list_item)
    await session.commit()
    await session.refresh(db_list_item)
    return db_list_item


async def craete_multiple_list_items(session: AsyncSession, list_items: list[str], to_do_list: List) -> list[ListItem]:
    """
    Creates multiple list items in the list and stores them in the db
    """
    items : list['ListItem'] = []
    for item in list_items:
        items.append(create_list_item(session, item, to_do_list.id)) #type: ignore
    
    session.add(to_do_list)
    await session.commit()
    await session.refresh(to_do_list)
    
    return items


def get_list_item_by_id(list_item_id: int, list: List) -> ListItem | None:
    """
    Searches for the list item by its id within the list and returns it if found, otherwise returns None
    """
    if list.list_items is None:
        return None
    for item in list.list_items:
        if item.id == list_item_id:
            return item
    else:
        return None

async def update_list_item(session: AsyncSession, list_item_id: int, list: List, updated_list_item: ListItemUpdate) -> ListItem | None:
    """
    Updates the list item by its id within the list and save it in the database.
    Returns the updated list item if successful, otherwise returns None.
    """
    list_item = get_list_item_by_id(list_item_id, list)
    if list_item is None:
        return None
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

async def delete_list_Item(session: AsyncSession, list_item_id: int, list: List) -> None:
    """
    Deletes the list item by its id within the list.
    """
    list_item = get_list_item_by_id(list_item_id, list)
    if list_item is None:
        raise ListItemNotFoundException()
    await session.delete(list_item)
    await session.commit()