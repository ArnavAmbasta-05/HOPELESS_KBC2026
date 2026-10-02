"""KoreX API — Notion Integration Router (Sprint 6, TAD §14, §27.4, INT-NOT-001..009)."""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from integrations.notion.adapter import NotionAdapter
from integrations.notion.commit_wiring import NotionCommitExecutor
from integrations.notion.conflict import StaleNotionProposalConflictError
from integrations.notion.dlq import DLQEntry, NotionDLQManager, NotionIntegrationIncident
from integrations.notion.webhooks import NotionWebhookReceiver, NotionWebhookVerificationError
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.contracts.notion import (
    NotionHealthStatus,
    NotionWebhookPayload,
    NotionWriteResult,
)
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from packages.contracts.auth import AuthUser

router = APIRouter(prefix="/api/v1/integrations/notion", tags=["Notion Integration"])

_adapter = NotionAdapter()
_webhook_receiver = NotionWebhookReceiver(adapter=_adapter)
_commit_executor = NotionCommitExecutor(adapter=_adapter)


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class CommitNotionRequest(BaseModel):
    proposal_id: str = Field(..., description="Approved proposal ID")
    is_approved: bool = Field(default=True, description="Approval flag")
    baseline_revision: int = Field(default=1, description="Baseline snapshot revision")
    baseline_timestamp: str = Field(default="2026-03-15T07:45:00Z", description="Baseline timestamp")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/webhooks",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Inbound Notion Webhook Receiver (HMAC-SHA256 verified + authoritative re-fetch)",
)
async def handle_notion_webhook(
    request: Request,
    payload: NotionWebhookPayload,
    notion_signature: str | None = Header(None, alias="Notion-Signature"),
) -> ResponseEnvelope[dict[str, Any]]:
    """Receives inbound Notion webhook events, verifies HMAC signature, and re-fetches authoritative state."""
    raw_body = await request.body()
    try:
        _webhook_receiver.verify_signature(raw_body, notion_signature or payload.signature)
    except NotionWebhookVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Webhook signature verification failed: {exc}",
        ) from exc

    result = await _webhook_receiver.process_webhook(payload)
    return make_success_envelope(data=result, request_id=str(uuid.uuid4()))


@router.get(
    "/health",
    response_model=ResponseEnvelope[NotionHealthStatus],
    summary="Probe Notion Adapter health and rate-limiter capacity",
)
async def check_notion_health(
    current_user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[NotionHealthStatus]:
    """Returns adapter health, token status, and token-bucket capacity."""
    health_status = await _adapter.health()
    return make_success_envelope(data=health_status, request_id=str(uuid.uuid4()))


@router.get(
    "/dlq",
    response_model=ResponseEnvelope[list[DLQEntry]],
    summary="List Notion Dead-Letter Queue (DLQ) entries",
)
async def list_dlq_entries(
    current_user: AuthUser = Depends(require_permission(Permission.ADMIN_AUDIT)),
) -> ResponseEnvelope[list[DLQEntry]]:
    """Returns DLQ entries for unrecoverable outbound Notion operations."""
    entries = _adapter.dlq_manager.list_entries()
    return make_success_envelope(data=entries, request_id=str(uuid.uuid4()))


@router.get(
    "/incidents",
    response_model=ResponseEnvelope[list[NotionIntegrationIncident]],
    summary="List active Notion integration incidents",
)
async def list_notion_incidents(
    current_user: AuthUser = Depends(require_permission(Permission.ADMIN_AUDIT)),
) -> ResponseEnvelope[list[NotionIntegrationIncident]]:
    """Returns operator-visible integration incidents."""
    incidents = _adapter.dlq_manager.list_incidents()
    return make_success_envelope(data=incidents, request_id=str(uuid.uuid4()))


@router.post(
    "/commit",
    response_model=ResponseEnvelope[NotionWriteResult],
    summary="Execute verified outbound Notion write plan (32 operations for golden disruption)",
)
async def execute_notion_commit(
    request: CommitNotionRequest,
    current_user: AuthUser = Depends(require_permission(Permission.PROPOSAL_APPROVE)),
) -> ResponseEnvelope[NotionWriteResult]:
    """Applies the approved change proposal write plan to Notion with conflict pre-check."""
    try:
        result = await _commit_executor.execute_commit(
            proposal_id=request.proposal_id,
            is_approved=request.is_approved,
            baseline_revision=request.baseline_revision,
            baseline_timestamp=request.baseline_timestamp,
        )
    except StaleNotionProposalConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return make_success_envelope(data=result, request_id=str(uuid.uuid4()))
