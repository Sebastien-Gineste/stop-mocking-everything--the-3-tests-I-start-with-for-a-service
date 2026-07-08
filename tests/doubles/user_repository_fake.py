from __future__ import annotations

from app.domain.models import User
from app.ports.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    def save(self, user: User) -> None:
        self.users[user.email] = user

    def find_by_email(self, email: str) -> User | None:
        return self.users.get(email)
