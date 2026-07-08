from __future__ import annotations

from app.domain.models import Payment, Result
from app.domain.validation import validate_amount
from app.ports.payment_gateway import PaymentGateway
from app.ports.payment_repository import PaymentRepository
from app.ports.user_repository import UserRepository
from app.services.payment_eligibility_checker import PaymentEligibilityChecker


class PaymentService:
    def __init__(
        self,
        user_repository: UserRepository,
        payment_repository: PaymentRepository,
        payment_gateway: PaymentGateway,
        eligibility_checker: PaymentEligibilityChecker | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._payment_repository = payment_repository
        self._payment_gateway = payment_gateway
        self._eligibility_checker = eligibility_checker or PaymentEligibilityChecker()

    def charge(self, email: str, amount: float, currency: str) -> Result[Payment]:
        amount_result = validate_amount(amount)
        if amount_result.is_error():
            return Result.fail(amount_result.error or "Invalid amount")

        user = self._user_repository.find_by_email(email)
        if user is None:
            return Result.fail("User not found")

        eligibility_result = self._eligibility_checker.ensure_eligible(amount, currency)
        if eligibility_result.is_error():
            return Result.fail(eligibility_result.error or "Payment not eligible")

        pending = Payment(
            user_email=email,
            amount=amount,
            currency=currency,
            transaction_id="",
            status="pending",
        )
        try:
            charge_result = self._payment_gateway.charge(pending)
        except Exception:
            return Result.fail("Payment gateway unavailable")

        if charge_result.status != "succeeded":
            return Result.fail("Payment failed")

        payment = Payment(
            user_email=email,
            amount=amount,
            currency=currency,
            transaction_id=charge_result.transaction_id,
            status=charge_result.status,
        )
        self._payment_repository.save(payment)
        return Result.ok(payment)
