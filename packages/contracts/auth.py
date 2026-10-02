"""Auth contracts: AuthUser model and AuthProvider protocol.

Defines the abstract interface that all authentication providers must implement,
and the canonical AuthUser model used across the platform.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class AuthUser(BaseModel):
    """Authenticated user identity with role and event scope.

    Attributes:
        user_id: Unique identifier for the user.
        email: User email address.
        name: Display name.
        roles: List of role slugs (see services.api.auth.rbac.Role).
        event_id: Optional event scope; when set, the user can only access
            resources belonging to this event (BR-018 isolation).
    """

    user_id: str
    email: str
    name: str
    roles: list[str] = Field(default_factory=list)
    event_id: str | None = None


@runtime_checkable
class AuthProvider(Protocol):
    """Abstract authentication provider interface.

    All auth backends (OIDC/SSO, dev-login, etc.) must satisfy this protocol.
    """

    async def verify_token(self, token: str) -> AuthUser:
        """Verify a bearer token and return the authenticated user.

        Raises:
            ValueError: If the token is invalid, expired, or malformed.
        """
        ...

    async def get_login_url(self, redirect_uri: str) -> str:
        """Return the URL to redirect the user to for authentication."""
        ...
