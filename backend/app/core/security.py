from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password to its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain-text password for storage."""
    validate_password_length(password)
    return pwd_context.hash(password)


def _create_token(
    *,
    token_type: str,
    subject: str,
    expires_delta: timedelta,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "type": token_type,
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
    }
    if additional_claims:
        payload.update(additional_claims)

    secret = settings.jwt_secret_key.get_secret_value()
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def create_access_token(
    subject: str,
    *,
    expires_minutes: Optional[int] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a short-lived access token."""
    minutes = expires_minutes or settings.access_token_expire_minutes
    return _create_token(
        token_type="access",
        subject=subject,
        expires_delta=timedelta(minutes=minutes),
        additional_claims=additional_claims,
    )


def create_refresh_token(
    subject: str,
    *,
    expires_minutes: Optional[int] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a long-lived refresh token."""
    minutes = expires_minutes or settings.refresh_token_expire_minutes
    return _create_token(
        token_type="refresh",
        subject=subject,
        expires_delta=timedelta(minutes=minutes),
        additional_claims=additional_claims,
    )


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a token and return its payload. Raises JWTError on failure."""
    secret = settings.jwt_secret_key.get_secret_value()
    return jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])


def validate_password_length(password: str) -> None:
    """Ensure password is within bcrypt's 72-byte limit."""
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password exceeds bcrypt 72-byte limit.")


__all__ = [
    "JWTError",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_password_hash",
    "validate_password_length",
    "verify_password",
]

