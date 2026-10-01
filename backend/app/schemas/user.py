from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.common.enums import UserRole


class UserResponse(BaseModel):
    """
    Safe user representation returned by the API.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime
