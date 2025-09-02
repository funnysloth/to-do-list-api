# Imports from external libraries
from sqlmodel import Session

# Imports from app modules
from app.models.list_item import ListItem, ListItemCreate, ListItemUpdate
from app.models.list import List


def create_list_item(session: Session, list_item: ListItemCreate, list_id: int) -> ListItem:
    """
    Creates a new list item in the list and stores it in the db
    """
    list_item_dict = list_item.model_dump()
    list_item_dict["list_id"] = list_id
    db_list_item = ListItem.model_validate(list_item_dict)
    session.add(db_list_item)
    session.commit()
    session.refresh(db_list_item)
    return db_list_item


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

def update_list_item(session: Session, list_item_id: int, list: List, updated_list_item: ListItemUpdate) -> ListItem | None:
    """
    Updates the list item by its id within the list and save it in the database.
    Returns the updated list item if successful, otherwise returns None.
    """
    list_item = get_list_item_by_id(list_item_id, list)
    if list_item is None:
        return None
    new_data = updated_list_item.model_dump(exclude_unset=True)
    list_item.sqlmodel_update(new_data)
    session.add(list_item)
    session.commit()
    session.refresh(list_item)
    return list_item

def delete_list_Item(session: Session, list_item_id: int, list: List) -> None:
    """
    Deletes the list item by its id within the list.
    """
    list_item = get_list_item_by_id(list_item_id, list)
    if list_item is None:
        return None
    session.delete(list_item)
    session.commit()