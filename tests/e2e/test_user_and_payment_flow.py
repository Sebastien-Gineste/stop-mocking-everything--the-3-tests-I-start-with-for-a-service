from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.adapters.real_implementation.http_payment_gateway import HttpPaymentGateway
from app.container import create_test_container
from app.db import create_connection
from app.main import create_app

DEFAULT_EMAIL = "john@example.com"
DEFAULT_PASSWORD = "secure-password"


# -----------------------------------------------------------------------------
# SUT — full app stack (real SQLite + DI + HttpPaymentGateway over Docker payment provider)
# -----------------------------------------------------------------------------


def create_e2e_client(tmp_path: Path, payment_provider_url: str) -> TestClient:
    db_path = tmp_path / "test.db"
    connection = create_connection(str(db_path))
    container = create_test_container(
        connection=connection,
        payment_gateway=HttpPaymentGateway(base_url=payment_provider_url),
    )
    app = create_app(container=container)
    return TestClient(app)


# -----------------------------------------------------------------------------
# Test helpers — reusable HTTP payloads
# -----------------------------------------------------------------------------


def register_user_payload(
    email: str = DEFAULT_EMAIL,
    password: str = DEFAULT_PASSWORD,
) -> dict[str, str]:
    return {"email": email, "password": password}


def charge_payment_payload(
    email: str = DEFAULT_EMAIL,
    amount: float = 25.0,
    currency: str = "EUR",
) -> dict[str, str | float]:
    return {"email": email, "amount": amount, "currency": currency}


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def client(tmp_path, payment_provider_url: str) -> TestClient:
    with create_e2e_client(tmp_path, payment_provider_url) as test_client:
        yield test_client


# -----------------------------------------------------------------------------
# Tests — main user flows over real HTTP wiring
# -----------------------------------------------------------------------------


@pytest.mark.e2e
def test_user_can_register_and_be_retrieved(client: TestClient):
    response = client.post("/users", json=register_user_payload())

    assert response.status_code == 201
    assert response.json()["email"] == DEFAULT_EMAIL

    user_response = client.get(f"/users/{DEFAULT_EMAIL}")

    assert user_response.status_code == 200
    assert user_response.json()["email"] == DEFAULT_EMAIL


@pytest.mark.e2e
def test_user_can_make_payment_and_list_it(client: TestClient):
    client.post("/users", json=register_user_payload())

    payment_response = client.post("/payments", json=charge_payment_payload())

    assert payment_response.status_code == 201
    payload = payment_response.json()
    assert payload["status"] == "succeeded"
    assert payload["transaction_id"].startswith("stub-txn-")

    payments_response = client.get(f"/payments/{DEFAULT_EMAIL}")

    assert payments_response.status_code == 200
    payments = payments_response.json()
    assert len(payments) == 1
    assert payments[0]["amount"] == 25.0
