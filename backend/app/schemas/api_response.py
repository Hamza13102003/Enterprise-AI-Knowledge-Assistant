from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    """
    Standard success response.
    """

    success: bool = True
    message: str
    data: Any
