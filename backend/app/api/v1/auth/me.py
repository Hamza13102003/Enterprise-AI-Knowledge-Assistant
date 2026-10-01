from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.database.models.user import User
from app.schemas.api_response import APIResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=APIResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    """
    Return the currently authenticated user.
    """
    return APIResponse(
        message="Authenticated user retrieved successfully.",
        data=UserResponse.model_validate(current_user),
    )
