from __future__ import annotations

from app.domain.models import ChargeResult, Payment
from app.ports.payment_gateway import PaymentGateway


class PaymentGatewayDownStub(PaymentGateway):
    """Stub used to force a gateway-down scenario in tests."""

    def charge(self, _payment: Payment) -> ChargeResult:
        raise RuntimeError("Gateway is down")
