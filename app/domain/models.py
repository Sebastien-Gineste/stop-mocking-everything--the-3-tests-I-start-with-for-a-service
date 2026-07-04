from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class User:
    email: str
    password_hash: str


@dataclass(frozen=True)
class Payment:
    user_email: str
    amount: float
    currency: str
    transaction_id: str
    status: str


@dataclass(frozen=True)
class ChargeResult:
    transaction_id: str
    status: str


@dataclass(frozen=True)
class Result(Generic[T]):
    value: T | None = None
    error: str | None = None

    @classmethod
    def ok(cls, value: T) -> Result[T]:
        return cls(value=value)

    @classmethod
    def fail(cls, error: str) -> Result[T]:
        return cls(error=error)

    def is_ok(self) -> bool:
        return self.error is None

    def is_error(self) -> bool:
        return self.error is not None

    def unwrap(self) -> T:
        if self.error is not None:
            raise ValueError(self.error)
        assert self.value is not None
        return self.value
