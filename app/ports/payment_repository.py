from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import Payment


class PaymentRepository(ABC):
    @abstractmethod
    def save(self, payment: Payment) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user_email(self, email: str) -> list[Payment]:
        raise NotImplementedError
