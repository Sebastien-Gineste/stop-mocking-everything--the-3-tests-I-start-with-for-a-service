from __future__ import annotations

import pytest

from app.adapters.fakes.fake_payment_repository import FakePaymentRepository
from app.adapters.real_implementation.sqlite_payment_repository import (
    SqlitePaymentRepository,
)
from app.domain.models import Payment
from app.db import create_connection
from app.ports.payment_repository import PaymentRepository


# -----------------------------------------------------------------------------
# Contract — same promise exercised against fake AND real adapters
# -----------------------------------------------------------------------------


def payment_repository_contract(repository: PaymentRepository) -> None:
    payment = Payment(
        user_email="john@example.com",
        amount=42.0,
        currency="EUR",
        transaction_id="txn-1",
        status="succeeded",
    )

    repository.save(payment)

    saved_payments = repository.find_by_user_email("john@example.com")

    assert len(saved_payments) == 1
    assert saved_payments[0].amount == 42.0
    assert saved_payments[0].currency == "EUR"
    assert saved_payments[0].transaction_id == "txn-1"
    assert saved_payments[0].status == "succeeded"


# -----------------------------------------------------------------------------
# SUT setup — one factory per adapter implementation
# -----------------------------------------------------------------------------


def create_fake_payment_repository_sut() -> PaymentRepository:
    return FakePaymentRepository()


def create_sqlite_payment_repository_sut() -> PaymentRepository:
    connection = create_connection()
    return SqlitePaymentRepository(connection)


# -----------------------------------------------------------------------------
# Tests — fake vs real, same contract
# -----------------------------------------------------------------------------


@pytest.mark.contract
def test_fake_payment_repository_contract():
    repository = create_fake_payment_repository_sut()

    payment_repository_contract(repository)


@pytest.mark.contract
def test_sqlite_payment_repository_contract():
    repository = create_sqlite_payment_repository_sut()

    payment_repository_contract(repository)
