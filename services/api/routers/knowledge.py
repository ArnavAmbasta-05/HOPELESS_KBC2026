"""RAG & Institutional Memory API Router (Sprint 9, FR-KB-001..003, RULE-10, TAD §13)."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from packages.contracts.knowledge import (
    DocumentChunk,
    DocumentSourceType,
    KnowledgeItem,
    PostEventReport,
    RAGQuery,
    RAGResponse,
)
from services.workers.rag.service import RAGKnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
rag_service = RAGKnowledgeService()


class IngestDocRequest(BaseModel):
    document_id: str
    title: str
    source_type: DocumentSourceType
    content: str
    tags: list[str] = Field(default_factory=list)
    tenant_id: str = "kiit_fest_ops"
    event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SynthesizeReportRequest(BaseModel):
    event_id: str
    event_name: str
    telemetry: dict[str, Any] = Field(default_factory=dict)


class CreateKnowledgeItemRequest(BaseModel):
    tenant_id: str = "kiit_fest_ops"
    source_event_id: str
    category: str
    title: str
    problem_statement: str
    resolution_strategy: str
    tags: list[str] = Field(default_factory=list)


@router.post("/query", response_model=RAGResponse)
async def query_knowledge_base(req: RAGQuery) -> RAGResponse:
    """Performs scoped grounded RAG retrieval with citations (RULE-10, TAD §13)."""
    return rag_service.query(req)


@router.post("/ingest", response_model=list[DocumentChunk])
async def ingest_document(req: IngestDocRequest) -> list[DocumentChunk]:
    """Ingests and chunks operational SOPs or incident logs with tenant/event scoping."""
    return rag_service.ingest_document(
        document_id=req.document_id,
        title=req.title,
        source_type=req.source_type,
        content=req.content,
        tags=req.tags,
        tenant_id=req.tenant_id,
        event_id=req.event_id,
        metadata=req.metadata,
    )


@router.post("/post-event-report", response_model=PostEventReport)
async def generate_post_event_report(req: SynthesizeReportRequest) -> PostEventReport:
    """Synthesizes comprehensive Post-Event Operational Report (FR-KB-001, AT-10)."""
    return rag_service.synthesize_post_event_report(
        event_id=req.event_id,
        event_name=req.event_name,
        telemetry=req.telemetry,
    )


@router.get("/post-event-reports", response_model=list[PostEventReport])
async def list_post_event_reports() -> list[PostEventReport]:
    """Lists generated post-event operational reports."""
    return list(rag_service.post_event_reports.values())


@router.post("/items", response_model=KnowledgeItem)
async def create_knowledge_item(req: CreateKnowledgeItemRequest) -> KnowledgeItem:
    """Creates a curated institutional knowledge item (FR-KB-002, AT-10)."""
    return rag_service.generate_knowledge_item(
        tenant_id=req.tenant_id,
        source_event_id=req.source_event_id,
        category=req.category,
        title=req.title,
        problem_statement=req.problem_statement,
        resolution_strategy=req.resolution_strategy,
        tags=req.tags,
    )


@router.get("/items", response_model=list[KnowledgeItem])
async def list_knowledge_items() -> list[KnowledgeItem]:
    """Lists reusable institutional knowledge playbooks."""
    return rag_service.knowledge_items
