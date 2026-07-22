from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard response envelope for all API endpoints."""
    success: bool = True
    message: str = "Success"
    data: T | None = None
    pagination: dict | None = None