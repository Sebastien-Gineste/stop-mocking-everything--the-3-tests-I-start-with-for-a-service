"""
ANTI-PATTERN: mock-heavy service tests.

These tests look serious and run fast, but they mostly prove that the current
implementation calls the expected methods in the expected order.

They do NOT prove that:
- the user was correctly saved
- the repository implementation works
- the service works with real infrastructure

If you refactor the service (e.g. emit a domain event instead of calling save
directly), behavior may still be correct but these tests will fail.

Compare with:
- tests/unit/          -> validation rules and service orchestration with fakes
- tests/contract/      -> adapter promises (fake vs real)
- tests/e2e/           -> real wiring
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from app.services.user_service import UserService

DEFAULT_EMAIL = "john@example.com"
DEFAULT_PASSWORD = "secure-password"


# -----------------------------------------------------------------------------
# SUT — mock repository; with_user() simulates an existing user by email
# -----------------------------------------------------------------------------


@dataclass
class SUT:
    """SUT - System under test for the user service (mock-heavy anti-pattern)."""

    service: UserService
    repository: Mock


class SUTBuilder:
    def __init__(self) -> None:
        self.repository = Mock()
        self.repository.find_by_email.return_value = None

    def with_user(self, email: str = DEFAULT_EMAIL) -> SUTBuilder:
        def find_by_email(requested_email: str):
            if requested_email == email:
                return Mock()
            return None

        self.repository.find_by_email.side_effect = find_by_email
        return self

    def build(self) -> SUT:
        return SUT(service=UserService(self.repository), repository=self.repository)


def sut_builder() -> SUTBuilder:
    return SUTBuilder()


# -----------------------------------------------------------------------------
# Tests — assert method calls, not real behavior (compare with tests/unit/)
# -----------------------------------------------------------------------------


@pytest.mark.antipattern
def test_create_user_mock_heavy():
    sut = sut_builder().build()

    result = sut.service.register_user(DEFAULT_EMAIL, DEFAULT_PASSWORD)

    assert result.is_ok()
    sut.repository.find_by_email.assert_called_once_with(DEFAULT_EMAIL)
    sut.repository.save.assert_called_once()

    saved_user = sut.repository.save.call_args[0][0]
    assert saved_user.email == DEFAULT_EMAIL


@pytest.mark.antipattern
def test_create_user_duplicate_mock_heavy():
    sut = sut_builder().with_user(DEFAULT_EMAIL).build()

    result = sut.service.register_user(DEFAULT_EMAIL, DEFAULT_PASSWORD)

    assert result.is_error()
    sut.repository.find_by_email.assert_called_once_with(DEFAULT_EMAIL)
    sut.repository.save.assert_not_called()
