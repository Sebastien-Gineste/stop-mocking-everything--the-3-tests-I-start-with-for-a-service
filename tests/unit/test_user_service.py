from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.adapters.fakes.fake_user_repository import FakeUserRepository
from app.services.user_service import UserService

DEFAULT_EMAIL = "john@example.com"
DEFAULT_PASSWORD = "secure-password"


# -----------------------------------------------------------------------------
# SUT — builder wires contract-tested fakes; caller sets preconditions with with_user()
# -----------------------------------------------------------------------------


@dataclass
class SUT:
    """SUT - System under test for the user service."""

    service: UserService
    repository: FakeUserRepository


class SUTBuilder:

    def __init__(self) -> None:
        self.repository = FakeUserRepository()
        self.service = UserService(self.repository)

    def with_user(self, email: str, password: str = DEFAULT_PASSWORD) -> SUTBuilder:
        self.service.register_user(email, password)
        return self

    def build(self) -> SUT:
        return SUT(service=self.service, repository=self.repository)


def sut_builder() -> SUTBuilder:
    return SUTBuilder()


# -----------------------------------------------------------------------------
# Tests — service orchestration, assert on persisted state (not mock calls)
# -----------------------------------------------------------------------------


@pytest.mark.unit
def test_register_user_persists_in_fake_repository():
    sut = sut_builder().build()

    result = sut.service.register_user(DEFAULT_EMAIL, DEFAULT_PASSWORD)

    assert result.is_ok()
    saved = sut.repository.find_by_email(DEFAULT_EMAIL)
    assert saved is not None
    assert saved.email == DEFAULT_EMAIL


@pytest.mark.unit
def test_register_user_rejects_duplicate_email():
    sut = sut_builder().with_user(DEFAULT_EMAIL, DEFAULT_PASSWORD).build()

    result = sut.service.register_user(DEFAULT_EMAIL, "another-password")

    assert result.is_error()
    assert result.error == "User already exists"
    assert len(sut.repository.users) == 1


@pytest.mark.unit
def test_register_user_rejects_invalid_email():
    sut = sut_builder().build()

    result = sut.service.register_user("invalid-email", DEFAULT_PASSWORD)

    assert result.is_error()
    assert sut.repository.find_by_email("invalid-email") is None


@pytest.mark.unit
def test_register_user_rejects_short_password():
    sut = sut_builder().build()

    result = sut.service.register_user(DEFAULT_EMAIL, "short")

    assert result.is_error()
    assert sut.repository.find_by_email(DEFAULT_EMAIL) is None
