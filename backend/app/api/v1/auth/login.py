from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.schemas.api_response import APIResponse
from app.schemas.auth.login import LoginRequest
from app.schemas.auth.token import TokenResponse
from app.security.jwt import create_access_token
from app.security.password import verify_password

router = APIRouter()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    """
    Authenticate a user and return an access token.
    """
    repository = UserRepository(session)

    user = await repository.get_by_email(payload.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
    )

    token_response = TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

    return APIResponse(
        message="Login successful.",
        data=token_response,
    )
