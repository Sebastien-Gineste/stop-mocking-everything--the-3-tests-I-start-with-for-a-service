"""
ANTI-PATTERN: mock-heavy payment service tests.

These tests verify call plumbing more than behavior.
Compare with tests/unit/test_payment_service.py where the same service logic is
exercised with real collaborators and verified fakes at boundaries.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from app.domain.models import ChargeResult
from app.services.payment_service import PaymentService

DEFAULT_EMAIL = "john@example.com"


# NOTE: This test intentionally demonstrates a mock-only anti-pattern.
# It verifies call plumbing, but it does NOT validate:
# - gateway contract compatibility with the real HTTP adapter/provider
# - correctness of the actual payload sent over the wire
# - repository persistence/retrieval behavior against a real implementation
# - wiring concerns (DI, HTTP routes, DB schema/migrations)
# - behavior under collaborator changes that preserve method call shape
# What to test instead for confidence:
# - tests/contract/
# - tests/unit/test_payment_service.py
# - tests/e2e/test_user_and_payment_flow.py
@pytest.mark.antipattern
def test_charge_mock_heavy():
    user_repository = Mock()
    user_repository.find_by_email.return_value = Mock()
    payment_repository = Mock()
    payment_gateway = Mock()
    payment_gateway.charge.return_value = ChargeResult(
        transaction_id="txn-mock-1",
        status="succeeded",
    )
    service = PaymentService(user_repository, payment_repository, payment_gateway)

    result = service.charge(DEFAULT_EMAIL, 25.0, "EUR")

    assert result.is_ok()
    user_repository.find_by_email.assert_called_once_with(DEFAULT_EMAIL)
    payment_gateway.charge.assert_called_once()
    payment_repository.save.assert_called_once()


@pytest.mark.antipattern
def test_charge_user_missing_mock_heavy():
    user_repository = Mock()
    user_repository.find_by_email.return_value = None
    payment_repository = Mock()
    payment_gateway = Mock()
    service = PaymentService(user_repository, payment_repository, payment_gateway)

    result = service.charge("missing@example.com", 25.0, "EUR")

    assert result.is_error()
    user_repository.find_by_email.assert_called_once_with("missing@example.com")
    payment_gateway.charge.assert_not_called()
    payment_repository.save.assert_not_called()
