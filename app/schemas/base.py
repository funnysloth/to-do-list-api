from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class ResponseBase(BaseModel):
    message: str

class ResponseWithData(ResponseBase, Generic[T]):
    data: Optional[T] | None = None