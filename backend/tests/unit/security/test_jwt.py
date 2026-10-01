from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from app.core.settings import settings
from app.security.jwt import (
    JWT_ALGORITHM,
    create_access_token,
    decode_access_token,
)


def test_create_access_token_contains_expected_claims() -> None:
    user_id = str(uuid4())

    token = create_access_token(
        subject=user_id,
        role="user",
    )

    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[JWT_ALGORITHM],
    )

    assert payload["sub"] == user_id
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload


def test_decode_access_token_returns_payload() -> None:
    user_id = str(uuid4())

    token = create_access_token(
        subject=user_id,
        role="user",
    )

    payload = decode_access_token(token)

    assert payload["sub"] == user_id
    assert payload["role"] == "user"


def test_invalid_token_is_rejected() -> None:
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("this-is-not-a-valid-token")


def test_expired_token_is_rejected() -> None:
    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "user",
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
        },
        settings.secret_key,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)
