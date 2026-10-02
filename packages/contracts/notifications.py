"""Notification & Communications Data Contracts (Sprint 7, COM-001..008, TAD §19)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class ChannelType(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class CohortDefinition(BaseModel):
    """Audience cohort derived from affected sessions, venues, routes, or roles."""
    cohort_id: str = Field(default_factory=lambda: f"coh_{uuid.uuid4().hex[:8]}")
    name: str
    target_entity_type: str  # session, venue, transport_route, volunteer_role
    target_entity_id: str
    recipient_count: int
    participant_ids: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GroundedMessageDraft(BaseModel):
    """Message draft containing only approved facts (COM-003, RULE-02)."""
    draft_id: str = Field(default_factory=lambda: f"drf_{uuid.uuid4().hex[:8]}")
    cohort_id: str
    session_name: str
    old_state: str  # e.g. "Main Auditorium"
    new_state: str  # e.g. "Open Air Theatre"
    effective_time: str  # e.g. "09:00 AM"
    action_required: str  # e.g. "Proceed directly to Open Air Theatre (Campus 6)"
    message_text: str
    is_ai_draft: bool = True
    ai_label: str = "AI-GENERATED, unverified narrative; facts above are the source of truth"
    approved: bool = False
    approved_by: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DispatchRecord(BaseModel):
    """Record of a dispatched notification across channels."""
    dispatch_id: str = Field(default_factory=lambda: f"dsp_{uuid.uuid4().hex[:8]}")
    draft_id: str
    cohort_id: str
    channel: ChannelType
    recipient_id: str
    status: DeliveryStatus = DeliveryStatus.PENDING
    idempotency_key: str
    error_message: str | None = None
    sent_at: str | None = None
    delivered_at: str | None = None


class StaleCommunicationItem(BaseModel):
    """Public communication or signage referencing superseded facts (COM-007)."""
    item_id: str = Field(default_factory=lambda: f"stale_{uuid.uuid4().hex[:8]}")
    channel_or_location: str  # Instagram, Gate 1 Digital Board, Gate 3 Printed Sign
    superseded_entity: str  # "Main Auditorium", "Opening Ceremony"
    superseded_by: str  # "Open Air Theatre"
    message_snippet: str
    risk_severity: str = "HIGH"  # HIGH, MEDIUM, LOW
    action_recommended: str
    flagged_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
