from __future__ import annotations

from app.domain.models import Result


class PaymentEligibilityChecker:
    """Pure collaborator that decides whether a charge is allowed."""

    def __init__(
        self,
        *,
        max_amount: float = 1000.0,
        supported_currencies: tuple[str, ...] = ("EUR", "USD"),
    ) -> None:
        self._max_amount = max_amount
        self._supported_currencies = supported_currencies

    def ensure_eligible(self, amount: float, currency: str) -> Result[None]:
        if currency not in self._supported_currencies:
            return Result.fail("Unsupported currency")
        if amount > self._max_amount:
            return Result.fail("Amount exceeds limit")
        return Result.ok(None)
