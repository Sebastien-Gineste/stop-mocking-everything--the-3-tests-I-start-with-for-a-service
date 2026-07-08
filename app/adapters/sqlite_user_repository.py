from __future__ import annotations

import sqlite3

from app.domain.models import User
from app.ports.user_repository import UserRepository


class SqliteUserRepository(UserRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, user: User) -> None:
        self._connection.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
            ON CONFLICT(email) DO UPDATE SET password_hash = excluded.password_hash
            """,
            (user.email, user.password_hash),
        )
        self._connection.commit()

    def find_by_email(self, email: str) -> User | None:
        row = self._connection.execute(
            "SELECT email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if row is None:
            return None
        return User(email=row["email"], password_hash=row["password_hash"])
