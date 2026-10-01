from app.security.password import hash_password, verify_password


def test_hash_password_returns_different_value() -> None:
    password = "StrongPassword123!"

    password_hash = hash_password(password)

    assert password_hash != password


def test_verify_password_with_correct_password() -> None:
    password = "StrongPassword123!"

    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_verify_password_with_incorrect_password() -> None:
    password = "StrongPassword123!"

    password_hash = hash_password(password)

    assert verify_password("WrongPassword123!", password_hash) is False
