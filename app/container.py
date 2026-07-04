from __future__ import annotations

import sqlite3

from app.adapters.fakes.fake_payment_gateway import FakePaymentGateway
from app.adapters.real_implementation.sqlite_payment_repository import (
    SqlitePaymentRepository,
)
from app.adapters.real_implementation.sqlite_user_repository import SqliteUserRepository
from app.db import create_connection
from app.ports.payment_gateway import PaymentGateway
from app.ports.payment_repository import PaymentRepository
from app.ports.user_repository import UserRepository
from app.services.payment_service import PaymentService
from app.services.user_service import UserService


class Container:
    def __init__(
        self,
        connection: sqlite3.Connection | None = None,
        payment_gateway: PaymentGateway | None = None,
    ) -> None:
        self.connection = connection or create_connection("app.db")
        self.user_repository: UserRepository = SqliteUserRepository(self.connection)
        self.payment_repository: PaymentRepository = SqlitePaymentRepository(
            self.connection
        )
        self.payment_gateway: PaymentGateway = payment_gateway or FakePaymentGateway()
        self.user_service = UserService(self.user_repository)
        self.payment_service = PaymentService(
            self.user_repository,
            self.payment_repository,
            self.payment_gateway,
        )


def create_test_container(
    connection: sqlite3.Connection,
    payment_gateway: PaymentGateway | None = None,
) -> Container:
    return Container(connection=connection, payment_gateway=payment_gateway)


def create_in_memory_container() -> Container:
    return Container(
        connection=create_connection(),
        payment_gateway=FakePaymentGateway(),
    )
