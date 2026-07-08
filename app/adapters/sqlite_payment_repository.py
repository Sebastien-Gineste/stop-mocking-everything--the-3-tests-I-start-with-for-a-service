from __future__ import annotations

import sqlite3

from app.domain.models import Payment
from app.ports.payment_repository import PaymentRepository


class SqlitePaymentRepository(PaymentRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, payment: Payment) -> None:
        self._connection.execute(
            """
            INSERT INTO payments (user_email, amount, currency, transaction_id, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payment.user_email,
                payment.amount,
                payment.currency,
                payment.transaction_id,
                payment.status,
            ),
        )
        self._connection.commit()

    def find_by_user_email(self, email: str) -> list[Payment]:
        rows = self._connection.execute(
            """
            SELECT user_email, amount, currency, transaction_id, status
            FROM payments
            WHERE user_email = ?
            ORDER BY id
            """,
            (email,),
        ).fetchall()
        return [
            Payment(
                user_email=row["user_email"],
                amount=row["amount"],
                currency=row["currency"],
                transaction_id=row["transaction_id"],
                status=row["status"],
            )
            for row in rows
        ]
