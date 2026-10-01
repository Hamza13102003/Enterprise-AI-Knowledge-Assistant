from fastapi import APIRouter

from app.core.settings import settings
from app.exceptions.custom_exceptions import ResourceNotFoundException
from app.schemas.api_response import APIResponse
from app.utils.response import success_response

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> APIResponse:
    return success_response(
        message="Health check successful",
        data={
            "status": "healthy",
            "environment": settings.app_env,
        },
    )


@router.get("/test-error")
async def test_error() -> APIResponse:
    raise ResourceNotFoundException(
        resource="Document",
        resource_id="123",
    )
