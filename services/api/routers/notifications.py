"""KoreX API — Notifications & Communications Router (Sprint 7, TAD §19, COM-001..008)."""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.contracts.notifications import (
    ChannelType,
    CohortDefinition,
    DispatchRecord,
    GroundedMessageDraft,
    StaleCommunicationItem,
)
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from services.workers.notifications.service import MassDispatchRequiresApprovalError, NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications & Comms"])

_notification_service = NotificationService()


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class DispatchNotificationRequest(BaseModel):
    draft_id: str = Field(..., description="Grounded draft ID to dispatch")
    channel: ChannelType = Field(default=ChannelType.PUSH, description="Delivery channel")
    is_approved: bool = Field(default=False, description="Explicit approval flag")


class ApproveDraftRequest(BaseModel):
    draft_id: str = Field(..., description="Draft ID")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/cohorts",
    response_model=ResponseEnvelope[list[CohortDefinition]],
    summary="List derived participant cohorts for active disruptions",
)
async def list_cohorts(
    current_user: AuthUser = Depends(require_permission(Permission.NOTIFICATION_READ)),
) -> ResponseEnvelope[list[CohortDefinition]]:
    """Returns derived cohorts (e.g. 380 Opening, 230 Keynote, 180 Panel, 390 Valedictory)."""
    cohorts = _notification_service.get_impacted_cohorts()
    return make_success_envelope(data=cohorts, request_id=str(uuid.uuid4()))


@router.get(
    "/drafts",
    response_model=ResponseEnvelope[list[GroundedMessageDraft]],
    summary="List grounded message drafts",
)
async def list_drafts(
    current_user: AuthUser = Depends(require_permission(Permission.NOTIFICATION_READ)),
) -> ResponseEnvelope[list[GroundedMessageDraft]]:
    """Returns grounded drafts with old/new state, effective time, action required, and AI label."""
    drafts = _notification_service.get_drafts()
    return make_success_envelope(data=drafts, request_id=str(uuid.uuid4()))


@router.post(
    "/drafts/{draft_id}/approve",
    response_model=ResponseEnvelope[GroundedMessageDraft],
    summary="Approve a notification draft for mass dispatch",
)
async def approve_draft(
    draft_id: str,
    current_user: AuthUser = Depends(require_permission(Permission.PROPOSAL_APPROVE)),
) -> ResponseEnvelope[GroundedMessageDraft]:
    """Approves draft for mass dispatch."""
    try:
        draft = _notification_service.approve_draft(
            draft_id=draft_id,
            approved_by=current_user.email or current_user.user_id,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return make_success_envelope(data=draft, request_id=str(uuid.uuid4()))


@router.post(
    "/dispatch",
    response_model=ResponseEnvelope[list[DispatchRecord]],
    summary="Mass dispatch approved notifications to cohort",
)
async def dispatch_notification(
    request: DispatchNotificationRequest,
    current_user: AuthUser = Depends(require_permission(Permission.NOTIFICATION_SEND)),
) -> ResponseEnvelope[list[DispatchRecord]]:
    """Dispatches draft with approval gate check (RULE-03)."""
    try:
        records = await _notification_service.dispatch_notification(
            draft_id=request.draft_id,
            channel=request.channel,
            is_approved=request.is_approved,
        )
    except MassDispatchRequiresApprovalError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return make_success_envelope(data=records, request_id=str(uuid.uuid4()))


@router.get(
    "/stale",
    response_model=ResponseEnvelope[list[StaleCommunicationItem]],
    summary="Scan public communications and campus boards for superseded references",
)
async def scan_stale_communications(
    current_user: AuthUser = Depends(require_permission(Permission.NOTIFICATION_READ)),
) -> ResponseEnvelope[list[StaleCommunicationItem]]:
    """Scans and flags stale posts and directional signage (e.g. Instagram, Gate 1/3 boards)."""
    items = _notification_service.scan_stale_comms()
    return make_success_envelope(data=items, request_id=str(uuid.uuid4()))


@router.get(
    "/metrics",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Get aggregate delivery metrics across channels",
)
async def get_delivery_metrics(
    current_user: AuthUser = Depends(require_permission(Permission.NOTIFICATION_READ)),
) -> ResponseEnvelope[dict[str, Any]]:
    """Returns total, delivered, failed metrics and delivery rates."""
    metrics = _notification_service.dispatcher.get_delivery_metrics()
    return make_success_envelope(data=metrics, request_id=str(uuid.uuid4()))
