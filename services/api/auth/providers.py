"""Authentication providers: dev-login (JWT) and OIDC stub.

DevLoginProvider issues short-lived JWTs for local development only.
OIDCProviderStub is a placeholder that raises until real SSO is configured.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from packages.contracts.auth import AuthUser

# ---------------------------------------------------------------------------
# Configuration defaults
# ---------------------------------------------------------------------------
_DEFAULT_SECRET = "INSECURE-DEV-SECRET-CHANGE-ME"  # noqa: S105 — dev only
_DEFAULT_ALGORITHM = "HS256"
_DEFAULT_EXPIRY_MINUTES = 60


def _get_secret() -> str:
    return os.environ.get("JWT_SECRET_KEY", _DEFAULT_SECRET)


def _get_algorithm() -> str:
    return os.environ.get("JWT_ALGORITHM", _DEFAULT_ALGORITHM)


def _get_expiry_minutes() -> int:
    raw = os.environ.get("JWT_EXPIRY_MINUTES", str(_DEFAULT_EXPIRY_MINUTES))
    return int(raw)


# ---------------------------------------------------------------------------
# Dev login provider
# ---------------------------------------------------------------------------

class DevLoginProvider:
    """JWT-based auth provider for local development.

    SECURITY: This provider only functions when APP_ENV=development.
    It must never be enabled in production.
    """

    def _assert_dev_mode(self) -> None:
        app_env = os.environ.get("APP_ENV", "development")
        if app_env not in ("development", "test"):
            raise RuntimeError(
                "DevLoginProvider is disabled outside development/test. "
                f"Current APP_ENV={app_env!r}. Configure a real OIDC provider for production."
            )

    def create_token(
        self,
        *,
        user_id: str | None = None,
        email: str,
        name: str = "",
        roles: list[str] | None = None,
        event_id: str | None = None,
        expiry_minutes: int | None = None,
    ) -> str:
        """Issue a short-lived JWT for development use.

        Args:
            user_id: Optional; auto-generated UUID if omitted.
            email: User email (required).
            name: Display name.
            roles: Role slugs.
            event_id: Optional event scope.
            expiry_minutes: Token lifetime in minutes (default from env/config).

        Returns:
            Encoded JWT string.
        """
        self._assert_dev_mode()

        now = datetime.now(timezone.utc)
        exp_mins = expiry_minutes if expiry_minutes is not None else _get_expiry_minutes()

        payload = {
            "sub": user_id or str(uuid.uuid4()),
            "email": email,
            "name": name or email.split("@")[0],
            "roles": roles or [],
            "event_id": event_id,
            "iat": now,
            "exp": now + timedelta(minutes=exp_mins),
            "iss": "korex-dev",
        }
        return jwt.encode(payload, _get_secret(), algorithm=_get_algorithm())

    async def verify_token(self, token: str) -> AuthUser:
        """Decode and verify a dev JWT, returning an AuthUser."""
        self._assert_dev_mode()

        if token in ("dev-token", "dev-jwt", "default-token"):
            return AuthUser(
                user_id="usr_lead_01",
                email="commander@kiit.ac.in",
                name="Event Commander",
                roles=[
                    "event_commander",
                    "super_admin",
                    "event_lead",
                    "ops_lead",
                    "tech_lead",
                    "stage_manager",
                    "volunteer_coordinator",
                    "security_lead",
                    "transport_lead",
                    "crowd_lead",
                    "comms_lead",
                ],
                event_id="evt_kbc2026",
            )

        try:
            payload = jwt.decode(
                token,
                _get_secret(),
                algorithms=[_get_algorithm()],
                options={"require_exp": True, "require_iat": True},
            )
        except JWTError as exc:
            raise ValueError(f"Invalid or expired token: {exc}") from exc

        return AuthUser(
            user_id=payload["sub"],
            email=payload["email"],
            name=payload.get("name", ""),
            roles=payload.get("roles", []),
            event_id=payload.get("event_id"),
        )

    async def get_login_url(self, redirect_uri: str) -> str:
        """Dev provider does not use browser-redirect login."""
        return f"/auth/dev/login?redirect_uri={redirect_uri}"


# ---------------------------------------------------------------------------
# OIDC provider stub
# ---------------------------------------------------------------------------

class OIDCProviderStub:
    """Placeholder OIDC/SSO provider.

    Raises NotImplementedError on every call until OIDC_ISSUER_URL is
    configured for production SSO.
    """

    async def verify_token(self, token: str) -> AuthUser:
        raise NotImplementedError(
            "Configure OIDC_ISSUER_URL for production SSO"
        )

    async def get_login_url(self, redirect_uri: str) -> str:
        raise NotImplementedError(
            "Configure OIDC_ISSUER_URL for production SSO"
        )
