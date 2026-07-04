from __future__ import annotations

import re

from app.domain.models import Result

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> Result[str]:
    if not email or not _EMAIL_PATTERN.match(email):
        return Result.fail("Invalid email address")
    return Result.ok(email)


def validate_password(password: str) -> Result[str]:
    if len(password) < 8:
        return Result.fail("Password must be at least 8 characters")
    return Result.ok(password)


def validate_amount(amount: float) -> Result[float]:
    if amount <= 0:
        return Result.fail("Amount must be positive")
    return Result.ok(amount)
