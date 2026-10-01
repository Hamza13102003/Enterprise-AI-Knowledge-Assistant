from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import UserRole
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_and_get_user(db_session: AsyncSession) -> None:
    """
    Verify that a user can be created and retrieved from PostgreSQL.
    """
    repository = UserRepository(db_session)

    email = f"test-{uuid4()}@example.com"

    created_user = await repository.create(
        email=email,
        password_hash="test-password-hash",
        full_name="Integration Test User",
        role=UserRole.USER,
    )

    assert created_user.id is not None
    assert created_user.email == email
    assert created_user.full_name == "Integration Test User"
    assert created_user.role == UserRole.USER

    user_by_id = await repository.get_by_id(created_user.id)

    assert user_by_id is not None
    assert user_by_id.id == created_user.id

    user_by_email = await repository.get_by_email(email)

    assert user_by_email is not None
    assert user_by_email.id == created_user.id
