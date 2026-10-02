"""Auth router: dev login endpoint and auth utilities."""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, status

from services.api.auth.providers import DevLoginProvider

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class DevLoginRequest(BaseModel):
    """Request body for the dev login endpoint."""

    email: str
    name: str = ""
    roles: list[str] = Field(default_factory=list)
    event_id: str | None = None


class DevLoginResponse(BaseModel):
    """Response from the dev login endpoint."""

    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/dev/login",
    response_model=DevLoginResponse,
    summary="Dev-only login (issues a JWT)",
    description=(
        "Issues a short-lived JWT for local development. "
        "Disabled when APP_ENV is not 'development' or 'test'."
    ),
)
async def dev_login(body: DevLoginRequest) -> DevLoginResponse:
    """Issue a dev JWT. Only available in development/test environments."""
    provider = DevLoginProvider()
    try:
        token = provider.create_token(
            email=body.email,
            name=body.name,
            roles=body.roles,
            event_id=body.event_id,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return DevLoginResponse(access_token=token)
