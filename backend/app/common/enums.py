from enum import StrEnum


class UserRole(StrEnum):
    """User roles used for authorization."""

    ADMIN = "admin"
    USER = "user"
