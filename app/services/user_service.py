from __future__ import annotations

import hashlib

from app.domain.models import Result, User
from app.domain.validation import validate_email, validate_password
from app.ports.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def register_user(self, email: str, password: str) -> Result[User]:
        email_result = validate_email(email)
        if email_result.is_error():
            return Result.fail(email_result.error or "Invalid email")

        password_result = validate_password(password)
        if password_result.is_error():
            return Result.fail(password_result.error or "Invalid password")

        if self._repository.find_by_email(email) is not None:
            return Result.fail("User already exists")

        user = User(
            email=email,
            password_hash=self._hash_password(password),
        )
        self._repository.save(user)
        return Result.ok(user)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
