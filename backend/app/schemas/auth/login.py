from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str
