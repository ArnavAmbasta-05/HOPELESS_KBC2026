"""FastAPI dependencies for authentication and authorization."""

from __future__ import annotations

import logging
import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packages.contracts.auth import AuthProvider, AuthUser
from services.api.auth.providers import DevLoginProvider, OIDCProviderStub

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_auth_provider() -> AuthProvider:
    """Select the auth provider based on environment configuration.

    Returns DevLoginProvider for development/test, OIDCProviderStub otherwise.
    """
    app_env = os.environ.get("APP_ENV", "development")
    if app_env in ("development", "test"):
        return DevLoginProvider()
    return OIDCProviderStub()


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ] = None,
) -> AuthUser:
    """Extract and verify the Bearer token, returning the authenticated user.

    Raises:
        HTTPException 401: Missing, invalid, or expired token.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    provider = _resolve_auth_provider()
    try:
        user = await provider.verify_token(credentials.credentials)
    except (ValueError, NotImplementedError) as exc:
        logger.warning("Authentication failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    logger.info(
        "Authenticated user=%s email=%s roles=%s event_id=%s",
        user.user_id,
        user.email,
        user.roles,
        user.event_id,
    )
    return user
