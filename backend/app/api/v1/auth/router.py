from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.login import router as login_router
from app.api.v1.auth.me import router as me_router
from app.database.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.schemas.api_response import APIResponse
from app.schemas.auth.register import RegisterRequest
from app.schemas.user import UserResponse
from app.security.password import hash_password
from app.services.user_service import UserService

router = APIRouter()
router.include_router(login_router)
router.include_router(me_router)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse,
)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    """
    Register a new application user.
    """
    repository = UserRepository(session)
    service = UserService(repository)

    password_hash = hash_password(payload.password)

    try:
        user = await service.create_user(
            email=payload.email,
            password_hash=password_hash,
            full_name=payload.full_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    await session.commit()

    user_response = UserResponse.model_validate(user)

    return APIResponse(
        message="User registered successfully.",
        data=user_response,
    )
