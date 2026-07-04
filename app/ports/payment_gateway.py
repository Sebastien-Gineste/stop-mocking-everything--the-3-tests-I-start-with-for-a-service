from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import ChargeResult, Payment


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, payment: Payment) -> ChargeResult:
        raise NotImplementedError
