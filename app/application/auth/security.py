"""Password hashing and JWT token utilities."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    payload: Dict[str, Any],
    secret: str,
    algorithm: str = "HS256",
    expires_minutes: int = 60 * 24 * 7,  # 7 дней по умолчанию
) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(data, secret, algorithm=algorithm)


def decode_access_token(token: str, secret: str, algorithm: str = "HS256") -> Dict[str, Any]:
    """Raise JWTError if token is invalid or expired."""
    return jwt.decode(token, secret, algorithms=[algorithm])
