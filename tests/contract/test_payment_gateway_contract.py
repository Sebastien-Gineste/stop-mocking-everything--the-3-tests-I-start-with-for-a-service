from __future__ import annotations

import pytest

from app.adapters.fakes.fake_payment_gateway import FakePaymentGateway
from app.adapters.real_implementation.http_payment_gateway import HttpPaymentGateway
from app.domain.models import Payment
from app.ports.payment_gateway import PaymentGateway


# -----------------------------------------------------------------------------
# Contract — same promise exercised against fake AND real adapters
# -----------------------------------------------------------------------------


def payment_gateway_contract(gateway: PaymentGateway) -> None:
    payment = Payment(
        user_email="john@example.com",
        amount=10.0,
        currency="EUR",
        transaction_id="",
        status="pending",
    )

    result = gateway.charge(payment)

    assert result.transaction_id
    assert result.status == "succeeded"


# -----------------------------------------------------------------------------
# SUT setup — one factory per adapter implementation
# -----------------------------------------------------------------------------


def create_fake_payment_gateway_sut() -> PaymentGateway:
    return FakePaymentGateway()


def create_http_payment_gateway_sut(base_url: str) -> PaymentGateway:
    return HttpPaymentGateway(base_url=base_url)


# -----------------------------------------------------------------------------
# Tests — fake vs real (HTTP over Docker), same contract
# -----------------------------------------------------------------------------


@pytest.mark.contract
def test_fake_payment_gateway_contract():
    gateway = create_fake_payment_gateway_sut()

    payment_gateway_contract(gateway)


@pytest.mark.contract
def test_http_payment_gateway_contract(payment_provider_url: str):
    gateway = create_http_payment_gateway_sut(payment_provider_url)

    payment_gateway_contract(gateway)
