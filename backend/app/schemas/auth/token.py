from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Response schema containing an access token."""

    access_token: str
    token_type: str = "bearer"
