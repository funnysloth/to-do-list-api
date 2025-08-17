from app.models.list import List
from app.schemas.list import ListCreate, ListUpdate
from sqlmodel import select, Session

def get_list_by_id(session: Session, id: int) -> List | None:
    """Get a list by its ID."""
    return session.exec(select(List).where(List.id == id)).first()

def create_list(session: Session, list: ListCreate, user_id: int) -> List:
    """Create a new list."""
    db_list = List.model_validate(list)
    db_list.last_modified_at = db_list.created_at
    db_list.user_id = user_id
    session.add(db_list)
    session.commit()
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

def delete_list(session: Session, list: List) -> None:
    """Delete a list."""
    session.delete(list)
    session.commit()