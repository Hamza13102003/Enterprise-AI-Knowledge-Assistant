from uuid import UUID

from app.common.enums import UserRole
from app.database.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.password import verify_password


class UserService:
    """
    Business logic for application users.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieve a user by their unique identifier.
        """
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email address.
        """
        return await self.user_repository.get_by_email(email)

    async def create_user(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        """
        Create a new application user.
        """
        existing_user = await self.user_repository.get_by_email(email)

        if existing_user is not None:
            raise ValueError("A user with this email already exists.")

        return await self.user_repository.create(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
        )

    async def authenticate_user(
        self,
        *,
        email: str,
        password: str,
    ) -> User | None:
        """
        Authenticate a user using email and password.
        """
        user = await self.user_repository.get_by_email(email)

        if user is None:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user
