from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.settings import settings

JWT_ALGORITHM = "HS256"


def create_access_token(
    subject: str,
    role: str,
    expires_minutes: int | None = None,
) -> str:
    """
    Create a signed JWT access token.
    """
    expiration_minutes = (
        expires_minutes if expires_minutes is not None else settings.access_token_expire_minutes
    )

    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=expiration_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Raises:
        jwt.InvalidTokenError: If the token is invalid or expired.
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[JWT_ALGORITHM],
    )
