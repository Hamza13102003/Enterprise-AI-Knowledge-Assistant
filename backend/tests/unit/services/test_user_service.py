from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.common.enums import UserRole
from app.database.models.user import User
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_create_user() -> None:
    repository = AsyncMock()

    repository.get_by_email.return_value = None

    user = User(
        email="hamza@example.com",
        password_hash="hashed-password",
        full_name="Test User",
        role=UserRole.USER,
    )

    repository.create.return_value = user

    service = UserService(repository)

    result = await service.create_user(
        email="hamza@example.com",
        password_hash="hashed-password",
        full_name="Test User",
    )

    assert result.email == "hamza@example.com"
    assert result.full_name == "Test User"
    assert result.role == UserRole.USER

    repository.get_by_email.assert_awaited_once_with("hamza@example.com")

    repository.create.assert_awaited_once_with(
        email="hamza@example.com",
        password_hash="hashed-password",
        full_name="Test User",
        role=UserRole.USER,
    )

    @pytest.mark.asyncio
    async def test_create_user_rejects_duplicate_email() -> None:
        repository = AsyncMock()

        existing_user = User(
            id=uuid4(),
            email="existing@example.com",
            password_hash="hashed-password",
            full_name="Existing User",
            role=UserRole.USER,
        )

        repository.get_by_email.return_value = existing_user

        service = UserService(repository)

        with pytest.raises(ValueError, match="already exists"):
            await service.create_user(
                email="existing@example.com",
                password_hash="hashed-password",
                full_name="New User",
            )

        repository.get_by_email.assert_awaited_once_with("existing@example.com")

        repository.create.assert_not_awaited()
