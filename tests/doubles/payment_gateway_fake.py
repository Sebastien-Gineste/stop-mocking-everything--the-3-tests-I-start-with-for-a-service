from __future__ import annotations

from app.domain.models import ChargeResult, Payment
from app.ports.payment_gateway import PaymentGateway


class FakePaymentGateway(PaymentGateway):
    """Fake gateway with real behavior; also acts as a spy by recording charges."""

    def __init__(self) -> None:
        self.charges: list[Payment] = []
        self._counter = 0

    def charge(self, payment: Payment) -> ChargeResult:
        self._counter += 1
        self.charges.append(payment)
        return ChargeResult(
            transaction_id=f"fake-txn-{self._counter}",
            status="succeeded",
        )
