from __future__ import annotations

import pytest

from app.adapters.sqlite_user_repository import SqliteUserRepository
from app.domain.models import User
from app.db import create_connection
from app.ports.user_repository import UserRepository
from tests.doubles.user_repository_fake import FakeUserRepository


# -----------------------------------------------------------------------------
# Contract — same promise exercised against fake AND real adapters
# -----------------------------------------------------------------------------


def user_repository_contract(repository: UserRepository) -> None:
    user = User(email="john@example.com", password_hash="hashed")

    repository.save(user)

    saved_user = repository.find_by_email("john@example.com")

    assert saved_user is not None
    assert saved_user.email == "john@example.com"
    assert saved_user.password_hash == "hashed"
    assert repository.find_by_email("missing@example.com") is None


# -----------------------------------------------------------------------------
# SUT setup — one factory per adapter implementation
# -----------------------------------------------------------------------------


def create_fake_user_repository_sut() -> UserRepository:
    return FakeUserRepository()


def create_sqlite_user_repository_sut() -> UserRepository:
    connection = create_connection()
    return SqliteUserRepository(connection)


# -----------------------------------------------------------------------------
# Tests — fake vs real, same contract
# -----------------------------------------------------------------------------


@pytest.mark.contract
def test_fake_user_repository_contract():
    repository = create_fake_user_repository_sut()

    user_repository_contract(repository)


@pytest.mark.contract
def test_sqlite_user_repository_contract():
    repository = create_sqlite_user_repository_sut()

    user_repository_contract(repository)
