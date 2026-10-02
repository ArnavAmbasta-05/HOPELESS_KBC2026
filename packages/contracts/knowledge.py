"""Institutional Memory & RAG Knowledge Contracts (Sprint 9, FR-KB-001..003, RULE-10, TAD §13)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class DocumentSourceType(StrEnum):
    SOP = "sop"
    INCIDENT_LOG = "incident_log"
    POST_EVENT_REPORT = "post_event_report"
    LESSON_LEARNED = "lesson_learned"
    VENUE_SPEC = "venue_spec"
    POLICY = "policy"


class GroundingCitation(BaseModel):
    """Grounding citation for RAG retrieved context (TAD §13, RULE-10)."""
    document_id: str
    chunk_id: str
    source_title: str
    source_type: DocumentSourceType
    source_url: str | None = None
    record_id: str | None = None
    snippet: str
    relevance_score: float = 0.85


class DocumentChunk(BaseModel):
    """Vectorized / lexical document chunk with tenant and event isolation metadata."""
    chunk_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    document_id: str
    tenant_id: str = "kiit_fest_ops"
    event_id: str | None = None  # None indicates cross-event global SOP; non-None is scoped to specific event
    source_type: DocumentSourceType
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RAGQuery(BaseModel):
    """Scoped query for SOP/guidelines retrieval with strict event isolation."""
    query: str
    tenant_id: str = "kiit_fest_ops"
    event_id: str | None = None
    include_global_sops: bool = True
    top_k: int = 5


class RAGResponse(BaseModel):
    """RAG answer with full grounding citations (RULE-10: Non-authoritative, guidance only)."""
    answer: str
    is_guidance_only: bool = True
    citations: list[GroundingCitation] = Field(default_factory=list)
    confidence: float = 0.90


class PostEventReport(BaseModel):
    """Automated Post-Event Report synthesized from execution logs (FR-KB-001, AT-10)."""
    report_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:8]}")
    event_id: str
    event_name: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_sessions: int
    completed_sessions: int
    disruptions_count: int
    change_proposals_count: int
    approvals_count: int
    weather_hazards_count: int
    crowd_surges_count: int
    transport_shuttle_trips: int
    summary_of_incidents: list[dict[str, Any]] = Field(default_factory=list)
    key_metrics: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


class KnowledgeItem(BaseModel):
    """Curated institutional lesson learned reusable across future editions (FR-KB-002, AT-10)."""
    item_id: str = Field(default_factory=lambda: f"ki_{uuid.uuid4().hex[:8]}")
    tenant_id: str = "kiit_fest_ops"
    source_event_id: str
    category: str  # e.g., "WEATHER_RELOCATION", "POWER_BACKUP", "TRANSPORT_DISPATCH"
    title: str
    problem_statement: str
    resolution_strategy: str
    citations: list[GroundingCitation] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
