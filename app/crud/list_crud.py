# Imports from external libraries
from sqlmodel import select, Session

# Imports from app modules
from app.models.list import List, ListCreate, ListUpdate
from app.models.user import User
from app.crud.list_item_crud import craete_multiple_list_items

def get_list_by_id(session: Session, id: int) -> List | None:
    """Get a list by its ID."""
    return session.exec(select(List).where(List.id == id)).first()

def create_list(session: Session, list: ListCreate, user_id: int) -> List:
    """Create a new list."""
    list_dict = list.model_dump()
    list_dict["user_id"] = user_id
    db_list = List.model_validate(list_dict)
    db_list.last_modified_at = db_list.created_at
    session.add(db_list)
    session.commit()
    session.refresh(db_list)
    if list.list_items:
        craete_multiple_list_items(session, list.list_items, db_list.id) #type:ignore
    session.refresh(db_list)
    return db_list

def update_list(session: Session, list: List, list_updates:ListUpdate) -> List:

    """Update a list."""
    new_list_data = list_updates.model_dump(exclude_unset=True)
    list.sqlmodel_update(new_list_data)
    session.add(list)
    session.commit()
    session.refresh(list)
    return list

def delete_list(session: Session, list_id: int, user: User) -> None:
    """Delete a list."""
    list = get_user_list_by_id(user, list_id)
    session.delete(list)
    session.commit()

def get_user_list_by_id(user: User, list_id: int) -> List | None:
    """
    Searches for a list by its id within the user lists
    """
    if user.lists is None:
        return None
    for list in user.lists:
        if list.id == list_id:
            return list
    else:
        return None