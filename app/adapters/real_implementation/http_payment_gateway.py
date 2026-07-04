from __future__ import annotations

import httpx

from app.domain.models import ChargeResult, Payment
from app.ports.payment_gateway import PaymentGateway


class HttpPaymentGateway(PaymentGateway):
    def __init__(self, base_url: str, client: httpx.Client | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.Client()

    def charge(self, payment: Payment) -> ChargeResult:
        response = self._client.post(
            f"{self._base_url}/charge",
            json={
                "user_email": payment.user_email,
                "amount": payment.amount,
                "currency": payment.currency,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return ChargeResult(
            transaction_id=payload["transaction_id"],
            status=payload["status"],
        )
