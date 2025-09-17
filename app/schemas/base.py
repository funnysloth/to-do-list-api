# Imports from external library
from pydantic import BaseModel

# Imports from standard library
from typing import Generic, TypeVar

DataT = TypeVar("DataT")

class ResponseBase(BaseModel):
    message: str

class ResponseWithNoData(ResponseBase):
    data: None = None

class ResponseWithData(ResponseBase, Generic[DataT]):
    data: DataT

class ResponseWithPagination(ResponseBase, Generic[DataT]):
    data: DataT