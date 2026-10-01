from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import UserRole
from app.database.models.user import User


class UserRepository:
    """
    Repository responsible for database operations related to users.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieve a user by their UUID.
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str,
        role: UserRole,
    ) -> User:
        """
        Create and persist a new user.
        """
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
        )

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user
