"""Notion Integration Data Contracts (Sprint 6, TAD §14, §27.4, INT-NOT-001..009)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class NotionOperationType(StrEnum):
    CREATE_PAGE = "create_page"
    UPDATE_PAGE = "update_page"
    ARCHIVE_PAGE = "archive_page"
    UPDATE_RELATION = "update_relation"
    CREATE_DATABASE_ENTRY = "create_database_entry"


class NotionSyncCursor(BaseModel):
    """Cursor tracking position in Notion changelog."""
    cursor_id: str = Field(default_factory=lambda: f"cur_{uuid.uuid4().hex[:8]}")
    last_synced_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_edited_time: str | None = None
    workspace_id: str = "ws_notion_kbc2026_sandbox"
    database_cursors: dict[str, str] = Field(default_factory=dict)


class NotionPageChange(BaseModel):
    """Normalized page change retrieved from Notion."""
    page_id: str
    database_id: str
    entity_type: str  # venues, sessions, volunteers, tasks, proposals
    title: str
    properties: dict[str, Any]
    last_edited_time: str
    edited_by: str | None = None
    version: int = 1


class NotionWriteOperation(BaseModel):
    """Atomic write operation in a write plan."""
    operation_id: str = Field(default_factory=lambda: f"op_{uuid.uuid4().hex[:8]}")
    idempotency_key: str = Field(default_factory=lambda: f"idem_{uuid.uuid4().hex[:12]}")
    op_type: NotionOperationType
    target_database: str
    target_page_id: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    external_ref: str | None = None
    description: str = ""


class NotionWritePlan(BaseModel):
    """Structured collection of outbound Notion writes derived from an approved proposal."""
    plan_id: str = Field(default_factory=lambda: f"nplan_{uuid.uuid4().hex[:8]}")
    proposal_id: str
    event_id: str
    operations: list[NotionWriteOperation] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    target_workspace: str = "ws_notion_kbc2026_sandbox"


class NotionWriteResult(BaseModel):
    """Summary of executed write plan."""
    plan_id: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    operation_ids: list[str] = Field(default_factory=list)
    page_ids_written: dict[str, str] = Field(default_factory=dict)  # op_id -> page_id
    duration_seconds: float = 0.0
    status: str = "COMPLETED"  # COMPLETED, PARTIAL, FAILED
    error_details: list[dict[str, Any]] = Field(default_factory=list)


class NotionVerificationResult(BaseModel):
    """Post-write verification result across operation IDs."""
    verified: bool
    verified_count: int
    missing_count: int
    missing_ids: list[str] = Field(default_factory=list)
    checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NotionHealthStatus(BaseModel):
    """Notion adapter health probe result."""
    status: str  # HEALTHY, DEGRADED, UNREACHABLE
    workspace_id: str
    latency_ms: float
    token_valid: bool
    rate_limiter_tokens: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NotionConflictReport(BaseModel):
    """Conflict report from refresh-before-commit verification."""
    has_conflict: bool
    conflicting_pages: list[dict[str, Any]] = Field(default_factory=list)
    reason: str | None = None
    source_revision: int
    remote_revision: int


class NotionWebhookPayload(BaseModel):
    """Inbound webhook notification from Notion."""
    event_id: str
    event_type: str  # page.created, page.updated, page.deleted
    page_id: str
    database_id: str | None = None
    workspace_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signature: str | None = None
