"""Authentication service for JWT token management."""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config import settings


def verify_credentials(username: str, password: str) -> bool:
    """Verify admin credentials against environment variables."""
    return (
        username == settings.admin_username
        and password == settings.admin_password
    )


def create_access_token(username: str) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return username if valid."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
