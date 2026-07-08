from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.domain.models import User
from app.ports.payment_gateway import PaymentGateway
from app.services.payment_eligibility_checker import PaymentEligibilityChecker
from app.services.payment_service import PaymentService
from app.services.user_service import UserService
from tests.doubles.payment_gateway_down_stub import PaymentGatewayDownStub
from tests.doubles.payment_gateway_fake import FakePaymentGateway
from tests.doubles.payment_repository_fake import FakePaymentRepository
from tests.doubles.user_repository_fake import FakeUserRepository

DEFAULT_EMAIL = "john@example.com"
DEFAULT_PASSWORD = "secure-password"


# -----------------------------------------------------------------------------
# SUT — builder wires contract-tested fakes; caller sets preconditions with with_user()
# -----------------------------------------------------------------------------


@dataclass
class SUT:
    """SUT - System under test for the payment service."""

    service: PaymentService
    user_repository: FakeUserRepository
    payment_repository: FakePaymentRepository
    payment_gateway: PaymentGateway


class SUTBuilder:

    def __init__(self) -> None:
        self.user_repository = FakeUserRepository()
        self.payment_repository = FakePaymentRepository()
        self.payment_gateway: PaymentGateway = FakePaymentGateway()
        self.eligibility_checker = PaymentEligibilityChecker()

    def with_user(
        self,
        email: str = DEFAULT_EMAIL,
        password: str = DEFAULT_PASSWORD,
        *,
        registered: bool = True,
    ) -> SUTBuilder:
        if registered:
            UserService(self.user_repository).register_user(email, password)
        else:
            self.user_repository.save(User(email=email, password_hash=password))
        return self

    def build(self) -> SUT:
        service = PaymentService(
            self.user_repository,
            self.payment_repository,
            self.payment_gateway,
            self.eligibility_checker,
        )
        return SUT(
            service=service,
            user_repository=self.user_repository,
            payment_repository=self.payment_repository,
            payment_gateway=self.payment_gateway,
        )


def sut_builder() -> SUTBuilder:
    return SUTBuilder()


# -----------------------------------------------------------------------------
# Tests — service orchestration, assert on persisted state (not mock calls)
# -----------------------------------------------------------------------------


@pytest.mark.service
def test_charge_persists_payment_and_records_gateway_charge():
    sut = sut_builder().with_user(DEFAULT_EMAIL, DEFAULT_PASSWORD).build()

    result = sut.service.charge(DEFAULT_EMAIL, 25.0, "EUR")

    assert result.is_ok()
    payment = result.unwrap()
    assert payment.transaction_id == "fake-txn-1"
    assert payment.status == "succeeded"
    saved_payments = sut.payment_repository.find_by_user_email(DEFAULT_EMAIL)
    assert len(saved_payments) == 1
    assert saved_payments[0].amount == 25.0
    assert len(sut.payment_gateway.charges) == 1


@pytest.mark.service
def test_charge_fails_when_user_missing():
    sut = sut_builder().build()

    result = sut.service.charge("missing@example.com", 25.0, "EUR")

    assert result.is_error()
    assert result.error == "User not found"
    assert sut.payment_repository.find_by_user_email("missing@example.com") == []
    assert len(sut.payment_gateway.charges) == 0


@pytest.mark.service
def test_charge_fails_when_amount_invalid():
    sut = sut_builder().with_user(DEFAULT_EMAIL, "hashed", registered=False).build()

    result = sut.service.charge(DEFAULT_EMAIL, 0, "EUR")

    assert result.is_error()
    assert sut.payment_repository.find_by_user_email(DEFAULT_EMAIL) == []
    assert len(sut.payment_gateway.charges) == 0


@pytest.mark.service
def test_charge_fails_when_gateway_is_down():
    builder = sut_builder().with_user(DEFAULT_EMAIL, DEFAULT_PASSWORD)
    builder.payment_gateway = PaymentGatewayDownStub()
    sut = builder.build()

    result = sut.service.charge(DEFAULT_EMAIL, 25.0, "EUR")

    assert result.is_error()
    assert result.error == "Payment gateway unavailable"
    assert sut.payment_repository.find_by_user_email(DEFAULT_EMAIL) == []


@pytest.mark.service
def test_charge_fails_when_currency_not_supported():
    sut = sut_builder().with_user(DEFAULT_EMAIL, DEFAULT_PASSWORD).build()

    result = sut.service.charge(DEFAULT_EMAIL, 25.0, "BTC")

    assert result.is_error()
    assert result.error == "Unsupported currency"
    assert sut.payment_repository.find_by_user_email(DEFAULT_EMAIL) == []
