from pydantic import BaseModel
from typing import Any

class ResponseBase(BaseModel):
    message: str
    data: dict[str, Any] | None= None