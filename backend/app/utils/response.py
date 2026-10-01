from typing import Any

from app.schemas.api_response import APIResponse


def success_response(
    message: str,
    data: Any,
) -> APIResponse:
    """
    Build a standardized success response.
    """
    return APIResponse(
        message=message,
        data=data,
    )
