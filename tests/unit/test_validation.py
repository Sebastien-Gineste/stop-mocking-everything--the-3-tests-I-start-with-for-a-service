from __future__ import annotations

import pytest

from app.domain.validation import validate_amount, validate_email, validate_password


# -----------------------------------------------------------------------------
# Tests — pure business rules, no dependencies, no SUT builder
# -----------------------------------------------------------------------------


@pytest.mark.unit
def test_user_cannot_register_with_invalid_email():
    result = validate_email("invalid-email")

    assert result.is_error()
    assert result.error == "Invalid email address"


@pytest.mark.unit
def test_user_can_register_with_valid_email():
    result = validate_email("john@example.com")

    assert result.is_ok()
    assert result.unwrap() == "john@example.com"


@pytest.mark.unit
def test_user_cannot_register_with_short_password():
    result = validate_password("short")

    assert result.is_error()
    assert result.error == "Password must be at least 8 characters"


@pytest.mark.unit
def test_user_can_register_with_valid_password():
    result = validate_password("secure-password")

    assert result.is_ok()


@pytest.mark.unit
def test_payment_amount_must_be_positive():
    result = validate_amount(0)

    assert result.is_error()
    assert result.error == "Amount must be positive"


@pytest.mark.unit
def test_payment_amount_accepts_positive_values():
    result = validate_amount(19.99)

    assert result.is_ok()
    assert result.unwrap() == 19.99
