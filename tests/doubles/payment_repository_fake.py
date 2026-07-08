from __future__ import annotations

from app.domain.models import Payment
from app.ports.payment_repository import PaymentRepository


class FakePaymentRepository(PaymentRepository):
    def __init__(self) -> None:
        self.payments: list[Payment] = []

    def save(self, payment: Payment) -> None:
        self.payments.append(payment)

    def find_by_user_email(self, email: str) -> list[Payment]:
        return [payment for payment in self.payments if payment.user_email == email]
