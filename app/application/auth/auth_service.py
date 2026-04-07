"""Authentication application service."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.auth.security import create_access_token, verify_password
from app.domain.entities.user import User
from app.domain.ports.user_repository import UserRepository


class InvalidCredentialsError(Exception):
    """Raised when phone/password pair does not match any active user."""


@dataclass(slots=True)
class LoginResult:
    access_token: str
    token_type: str
    user: User


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        jwt_secret: str,
        jwt_algorithm: str = "HS256",
        token_expires_minutes: int = 60 * 24 * 7,
    ) -> None:
        self._repo = user_repository
        self._secret = jwt_secret
        self._algorithm = jwt_algorithm
        self._expires = token_expires_minutes

    def login(self, phone: str, password: str) -> LoginResult:
        user = self._repo.get_by_phone(phone.strip())

        if user is None or not user.is_active:
            raise InvalidCredentialsError

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError

        token = create_access_token(
            payload={"sub": user.id, "role": user.role},
            secret=self._secret,
            algorithm=self._algorithm,
            expires_minutes=self._expires,
        )

        return LoginResult(access_token=token, token_type="bearer", user=user)
