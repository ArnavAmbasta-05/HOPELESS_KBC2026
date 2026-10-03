"""Governance API — super-admin-gated destructive actions.

Implements the rule: NO ONE can cancel an event without super-admin authority.
The cancellation is recorded in an append-only in-memory ledger (so it is
demonstrable without a database) and every attempt is auditable.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import require_super_admin

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])


class EventCancelRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class EventCancellationRecord(BaseModel):
    cancellation_id: str
    event_id: str
    reason: str
    cancelled_by: str
    cancelled_by_role: str
    cancelled_at: str


# Append-only in-memory ledger of cancellations.
_cancellations: list[EventCancellationRecord] = []


@router.get("/policy", summary="Describe governance policies")
async def get_policy() -> dict:
    return {
        "event_cancellation": {
            "rule": "Event cancellation requires super-admin authority.",
            "allowed_roles": ["super_admin"],
            "enforced_by": "require_super_admin (RBAC dependency) — 403 for everyone else",
            "audited": True,
        }
    }


@router.post(
    "/events/{event_id}/cancel",
    response_model=ResponseEnvelope[EventCancellationRecord],
    summary="Cancel an event (SUPER-ADMIN ONLY)",
)
async def cancel_event(
    request: Request,
    event_id: str,
    body: EventCancelRequest,
    user: AuthUser = Depends(require_super_admin()),
) -> ResponseEnvelope[EventCancellationRecord]:
    """Cancel an event. The require_super_admin dependency rejects any non
    super-admin with 403 before this handler runs."""
    record = EventCancellationRecord(
        cancellation_id=f"cxl_{uuid.uuid4().hex[:10]}",
        event_id=event_id,
        reason=body.reason,
        cancelled_by=user.user_id,
        cancelled_by_role="super_admin",
        cancelled_at=datetime.now(timezone.utc).isoformat(),
    )
    _cancellations.append(record)
    return make_success_envelope(
        data=record,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
    )


@router.get(
    "/cancellations",
    response_model=ResponseEnvelope[list[EventCancellationRecord]],
    summary="List event cancellations (audit ledger)",
)
async def list_cancellations(
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[EventCancellationRecord]]:
    return make_success_envelope(data=list(_cancellations), request_id=str(uuid.uuid4()))
